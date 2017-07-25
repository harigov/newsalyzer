#!/bin/sh
export GITHUB_TOKEN='6b32de5e1eab56b227ea24d49d58551114af77e6'
export GITHUB_RELEASE_TOOL=~/bin/github-release
export USER_NAME='harigov'
export REPOSITORY_NAME='newsalyzer'
export EXTENSION_VERSION='0.5.0'
export RELEASE_VERSION="v$EXTENSION_VERSION"
export RELEASE_NAME='Newsalyzer Browser Extension'
export RELEASE_DESCRIPTION='Initial version of the extension'

EXTENSION_FILE_NAME=$REPOSITORY_NAME
EXTENSION_FILE_NAME+='_'
EXTENSION_FILE_NAME+=$EXTENSION_VERSION

echo 'Create a new release tag in github'
$GITHUB_RELEASE_TOOL release --user $USER_NAME \
		--repo $REPOSITORY_NAME \
		--tag $RELEASE_VERSION \
		--name "$RELEASE_NAME" \
		--description "$RELEASE_DESCRIPTION" \
		--pre-release

echo 'Upload chrome version of the extension'
$GITHUB_RELEASE_TOOL upload --user $USER_NAME \
		--repo $REPOSITORY_NAME \
		--tag $RELEASE_VERSION \
		--name "$REPOSITORY_NAME-chrome-$EXTENSION_VERSION.crx" \
		--file "extension/output/$EXTENSION_FILE_NAME.crx"

echo 'Upload firefox version of the extension'
$GITHUB_RELEASE_TOOL upload --user $USER_NAME \
		--repo $REPOSITORY_NAME \
		--tag $RELEASE_VERSION \
		--name "$REPOSITORY_NAME-firefox-$EXTENSION_VERSION.xpi" \
		--file "extension/output/$EXTENSION_FILE_NAME.xpi"
