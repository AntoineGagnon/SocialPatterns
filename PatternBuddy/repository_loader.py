import datetime
import json
import logging
import re
import ssl
import subprocess

from constance import config
from django.core.exceptions import ObjectDoesNotExist
from github import Github, Repository as RepoAPI, UnknownObjectException
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig

from PatternBuddy.models import Repository, Language, PatternInRepo, DesignPattern, \
    ClassFileWithPattern, Contributor, Contribution

logger = logging.getLogger(__name__)


def analyze_repo(repo_api, repo_db):
    __java_analysis(repo_api, repo_db)

    output = subprocess.check_output(
        "cloc RepoStorage/" + repo_db.name + "/ --json",
        shell=True)

    repo_db.size = json.loads(output)['Java']['code']

    repo_db.dp_analyzed = True
    repo_db.save()

    pass


def get_repo_api(repository_name):
    repository_name = re.sub(r'^(http(s)*://)*github.com/', '', repository_name)
    g = Github("***REMOVED***")
    repo_api = g.get_repo(repository_name)
    return repo_api


def load_from_github(repository_name):
    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Loading from github")
    repo_api = get_repo_api(repository_name)

    try:
        full_name = repo_api.full_name
    except UnknownObjectException:
        return None
    repo = Repository(id=repo_api.id, full_name=full_name, name=repo_api.name)
    repo.language, created = Language.objects.get_or_create(name=repo_api.language)
    repo.save()
    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Getting contributors")
    contributor_counter = len(list(repo_api.get_contributors()))
    repo.contributors_count = contributor_counter

    if config.GET_CONTRIBUTORS_DATA:
        for contrib in repo_api.get_contributors():
            contributor_counter += 1
            try:
                contributor_db = Contributor.objects.get(login__exact=contrib.login)
            except ObjectDoesNotExist:
                contributor_db = Contributor()
                contributor_db.login = contrib.login
                contributor_db.followers_count = contrib.followers
                contributor_db.url = contrib.html_url
                contributor_db.save()

            contribution_db = Contribution(repository=repo,
                                           contributor=contributor_db,
                                           amount=contrib.contributions)
            contribution_db.save()

    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Getting pull request Data")

    if config.USE_BIGQUERY:
        pr_number = 0
        comments = 0
        bigquery_client: bigquery.Client = bigquery.Client.from_service_account_json("socialpatterns-c03d755a739c.json")
        dataset_ref = bigquery.DatasetReference("ghtorrent-bq", "ght_2018_04_01")
        dataset = bigquery_client.get_dataset(dataset_ref)
        repo_url_bigquery = repo_api.html_url.replace("github.com", "api.github.com/repos")
        queryconfig = QueryJobConfig()
        queryconfig.use_legacy_sql = False
        query_text = """ SELECT Count(*) AS Pull_Request , (SELECT Count(*) FROM `ghtorrent-bq.ght_2018_04_01.issue_comments`        WHERE  issue_id IN (SELECT id  FROM   `ghtorrent-bq.ght_2018_04_01.issues`  WHERE  pull_request_id IN (SELECT id FROM   `ghtorrent-bq.ght_2018_04_01.pull_requests` WHERE   base_repo_id = (SELECT id FROM   `ghtorrent-bq.ght_2018_04_01.projects` AS pj WHERE  pj.url ="%s" LIMIT 1  ))   )) AS Comments  FROM   `ghtorrent-bq.ght_2018_04_01.pull_requests` WHERE  base_repo_id =   (SELECT id   FROM   `ghtorrent-bq.ght_2018_04_01.projects` AS pj   WHERE  pj.url="%s" LIMIT 1   )  """ % (
            repo_url_bigquery, repo_url_bigquery)
        queryjob = bigquery_client.query(
            query_text
            , job_config=queryconfig)
        pr_number = list(queryjob.result())[0][0]
        comments = list(queryjob.result())[0][1]
    else:
        if config.CHECK_CLOSED_PR:
            pull_requests = repo_api.get_pulls(state="all")
        else:
            pull_requests = repo_api.get_pulls()

        pr_number = len(list(pull_requests))
        comments = 0

        for pr in pull_requests:
            try:
                comments += pr.comments
            except ssl.SSLError:
                logger.error("Read timeout when getting comments")
    repo.comments_count = comments
    repo.pull_request_count = pr_number

    repo.save()

    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Getting Design Pattern data")
    analyze_repo(repo_api, repo)
    repo.save()
    return repo


def get_file_from_repo(class_name, repo_name):
    try:
        output = subprocess.check_output(
            "ag -l --vimgrep -G=*.java '(class|interface) " + class_name + "' RepoStorage/" + repo_name + "/",
            shell=True)
    except subprocess.CalledProcessError:
        return "File not found"
    output = output.decode("utf-8")
    logger.debug("Command output: " + output)
    output = output.split("\n", 1)[0]
    logger.debug("Full filename: " + output)
    output = output.split("/", 2)[2]
    return output


def process_dpcore_output(output, repo_api, repo_db):
    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Cleaning up output")

    output = output.decode("utf-8")
    cleaned_lines = str(output).split("\n")

    current_dp = None
    current_pattern_in_repo = None
    for line in cleaned_lines:
        if re.match(r'^\s*$', line):
            continue
        else:
            if line.startswith("HyperCandidate"):
                if current_dp is not None:
                    current_pattern_in_repo.save()
                dp_name = line.replace("HyperCandidate of Pattern ", "").replace(":", "")

                current_dp, created = DesignPattern.objects.get_or_create(design_name=dp_name)
                current_pattern_in_repo = PatternInRepo.objects.create(design_pattern=current_dp, repository=repo_db)
                repo_db.dp_count += 1

            if line.startswith(("A", "B", "C", "D", "E")) and config.GET_PATTERN_CLASSES:

                p = re.compile("[A-Z]?\((.*)\): (.*)")
                p = p.search(line)

                class_name = p.group(2)

                # Find authors -> Show info about them
                if "[" in class_name:
                    for real_name in re.sub(r"[^a-zA-Z ]", "", class_name).split(" "):
                        if real_name != "":
                            if config.GET_FILES:
                                path = get_file_from_repo(real_name, repo_db.name)
                            else:
                                path = "Files were not collected for this DP"

                            class_file_with_pattern, created = ClassFileWithPattern.objects.get_or_create(
                                pattern_in_repo=current_pattern_in_repo, role=p.group(1), class_name=real_name,
                                url=path)
                            if config.GET_FILE_MODIFICATIONS_COUNT:
                                class_file_with_pattern.modifications_count = len(list(repo_api.get_commits(path=path)))
                                class_file_with_pattern.save()

                else:
                    if config.GET_FILES:
                        path = get_file_from_repo(class_name, repo_db.name)
                    else:
                        path = "Files were not collected for this DP"

                    class_file_with_pattern, created = ClassFileWithPattern.objects.get_or_create(
                        pattern_in_repo=current_pattern_in_repo, role=p.group(1), class_name=class_name,
                        url=path)
                    if config.GET_FILE_MODIFICATIONS_COUNT:
                        class_file_with_pattern.modifications_count = len(list(repo_api.get_commits(path=path)))
                        class_file_with_pattern.save()
    repo_db.save()


def __java_analysis(repo_api: RepoAPI, repo_db: Repository):
    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Cloning repo")
    subprocess.call(["git", "-C", "RepoStorage/", "clone", repo_api.clone_url])

    logger.debug(datetime.datetime.now().strftime("%H:%M:%S") + "Running DP-CORE")

    output = subprocess.check_output(
        "java -jar DP-CORE.jar -project=\"RepoStorage/" + repo_db.name + "\" -pattern=\"patterns/\"",
        shell=True)

    process_dpcore_output(output, repo_api, repo_db)
