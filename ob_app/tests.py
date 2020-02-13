from django.test import TestCase

# Create your tests here.
LANGUAGES_QUERY = {"query": "query repositoryOwner(login: \"Shopify\") { repositories(orderBy: {field: NAME, direction: ASC}, first: 100) {edges {node {idnamelanguages(first: 100) {nodes {name}}}cursor}pageInfo {endCursorhasNextPagestartCursor}}}"} #noqa
