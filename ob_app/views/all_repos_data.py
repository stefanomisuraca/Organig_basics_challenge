"""Retrive github informations using graphQL API."""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from ob_app.github import GhRequest
from django.conf import settings
import json
import itertools
import logging

logger = logging.getLogger('ob')

MOST_RECENT_REPOS_QUERY = { "query": "query {repositoryOwner(login: \"Shopify\") {repositories(orderBy: {field: CREATED_AT, direction: DESC}, first: 50) {edges {node {id name createdAt}}}}}"} #noqa
LANGUAGES_QUERY = {"query": "query {repositoryOwner(login: \"Shopify\") { repositories(orderBy: {field: NAME, direction: ASC}, first: 100) {edges {node {id name languages(first: 100) {nodes {name}}}cursor}pageInfo {endCursor hasNextPage startCursor}}}}"} #noqa
GH_GRAPHQL_ENDPOINT = settings.GH_GRAPHQL_ENDPOINT


class AllReposView(APIView):
    """Requires token authentication."""
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request):
        """Return data for all repos."""
        gh = GhRequest()
        most_recent_response = gh.post(
            GH_GRAPHQL_ENDPOINT,
            MOST_RECENT_REPOS_QUERY
        )

        def most_recent_generator(response_data):
            repos = response_data.get('data').get("repositoryOwner").get("repositories").get('edges')
            for repo in repos: #noqa
                node = repo.get('node')
                yield {"name": node.get('name'), "created_at": node.get('createdAt')}

        partial_languages_reponse = gh.post(
            GH_GRAPHQL_ENDPOINT,
            LANGUAGES_QUERY
        )
        languages_list = []
        has_next_page = partial_languages_reponse.get('data').get("repositoryOwner").get("repositories").get('pageInfo').get('hasNextPage')

        def languages(partial_languages_reponse):
            repos = partial_languages_reponse.get('data').get("repositoryOwner").get("repositories").get('edges')
            for repo in repos:
                languages = repo.get('node').get('languages').get('nodes')
                for language in languages:
                    yield language.get('name')
        languages_list.append(languages(partial_languages_reponse))

        while(has_next_page):
            cursor = partial_languages_reponse.get('data').get("repositoryOwner").get("repositories").get('edges')[-1].get('cursor')
            NEXT_LANGUAGES_QUERY = {"query": "query {repositoryOwner(login: \"Shopify\") { repositories(orderBy: {field: NAME, direction: ASC}, first: 100, after: \"%s\") {edges {node {id name languages(first: 100) {nodes {name}}}cursor}pageInfo {endCursor hasNextPage startCursor}}}}" % cursor} #noqa
            partial_languages_reponse = gh.post(
                GH_GRAPHQL_ENDPOINT,
                NEXT_LANGUAGES_QUERY
            )
            logger.info("REQUEST")
            logger.info(f"next_page {has_next_page}")
            logger.info(cursor)
            languages_list.append(languages(partial_languages_reponse))
            has_next_page = partial_languages_reponse.get('data').get("repositoryOwner").get("repositories").get('pageInfo').get('hasNextPage')

        all_languages_generators = itertools.chain(*languages_list)
        logger.info(all_languages_generators)
        all_languages = sorted(set(list(all_languages_generators)))

        return Response({
            "mostRecentRepos": [repo for repo in most_recent_generator(most_recent_response)],
            "languages": all_languages
        })
