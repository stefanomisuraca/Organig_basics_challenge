"""Retrive github informations using graphQL API."""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from ob_app.github import GhRequest
from django.conf import settings
from dateutil import parser
from datetime import date
import json
import itertools
import logging
logger = logging.getLogger('ob')

GH_GRAPHQL_ENDPOINT = settings.GH_GRAPHQL_ENDPOINT
COMMITS_COMMENT_DATE = date(2017, 1, 1)


class RepoView(APIView):
    """Requires token authentication."""
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, repo_name):
        language_repo_query = {"query": "query {repository(name: \"%s\", owner: \"Shopify\") {id languages(first: 100) {nodes {name id}}name}}" % repo_name}
        commit_comment_query = {"query": "query {repository(name: \"%s\", owner: \"Shopify\") {id name commitComments(first: 100) {edges {node {author {login} body createdAt}}}}}" % repo_name}

        gh = GhRequest()
        language_response = gh.post(
            GH_GRAPHQL_ENDPOINT,
            language_repo_query
        )
        languages = language_response.get('data').get("repository").get('languages').get('nodes')

        commit_comments_response = gh.post(
            GH_GRAPHQL_ENDPOINT,
            commit_comment_query
        )
        commits = commit_comments_response.get('data').get("repository").get('commitComments').get('edges')

        def comments_generator(commits):
            for commit in commits:
                logger.info(commit)
                created_at = parser.parse(commit.get('node').get('createdAt')).date()
                if created_at >= COMMITS_COMMENT_DATE:
                    yield {
                        "author": commit.get("node").get("author").get('login'),
                        "body": commit.get('node').get('body'),
                        "created_at": created_at
                    }

        return Response({
            "languages": [language.get('name') for language in languages],
            "comments": [comment for comment in comments_generator(commits)]
        })
