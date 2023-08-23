#!/bin/bash

set -o errexit

main() {
  check_args "$@"

  local image=$1
  local tag=$2

  local token=$(get_token $image)

  local digest=$(get_digest $image $tag $token)

  local blob=$(get_blob $image $token $digest)
  
  # Extract manifest
  echo "Label: manifest"
  jq '.config.Labels.manifest | fromjson' <<< "$blob"
  echo ""
  
  # Extract software quality
  echo "Label: sofware.quality"
  jq '.config.Labels."software.quality"' <<< "$blob"
  echo ""
}

# Obtain a token
get_token() {
  local image=$1

  echo "Retrieving ghcr token.
    IMAGE: $image
  " >&2

  curl \
    --silent \
    "https://ghcr.io/token?scope=repository:$image:pull" \
    | jq -r '.token'
}


# Retrieve the manifests, now specifying in the header
# that we have a token
get_digest() {
  local image=$1
  local tag=$2
  local token=$3

  echo "Retrieving image manifests.
    IMAGE:  $image
    TAG:    $tag
    TOKEN:  $token
  " >&2

  curl \
    --silent \
    --header "Accept: application/vnd.docker.distribution.manifest.v2+json" \
    --header "Authorization: Bearer $token" \
    "https://ghcr.io/v2/$image/manifests/$tag" \
    | jq -r '.config.digest'
}

get_blob() {
  local image=$1
  local token=$2
  local digest=$3

  echo "Retrieving blob.
    IMAGE:  $image
    TOKEN:  $token
    DIGEST: $digest
  " >&2

  curl \
    --silent \
    --location "https://ghcr.io/v2/$image/blobs/$digest" \
    --header "Authorization: Bearer $token" \
    | jq -r '.'
}

check_args() {
  if (($# != 2)); then
    echo "Error:
    Two arguments must be provided - $# provided.
  
    Usage:
      ./get-labels.sh <image> <tag>
      
Aborting."
    exit 1
  fi
}

main "$@"
