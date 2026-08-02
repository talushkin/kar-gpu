# Pending Queue Flow

This service is expected to poll the remote pending queue from:

- https://d23du7ibe4a1ni.cloudfront.net/pending.json

## Behavior

- The app checks the pending queue every 15 seconds.
- It processes the first pending video entry.
- After processing, it removes that video's metadata from the pending queue by calling the local cleanup endpoint.

## Cleanup API

Delete a single video from the local pending state:

```http
DELETE {{localUrl}}/api/pending
Content-Type: application/json

{
  "videoId": "kJQP7kiw5Fk"
}
```

A successful response looks like this:

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{
  "success": true,
  "deleted": 1,
  "count": 1,
  "url": "tracks/pending.json",
  "deletedIds": [
    "TEST_NEW_VID1"
  ]
}
```

Replace `{{localUrl}}` with the local app URL, for example:

```text
http://127.0.0.1:5000
```

## Expected Flow

1. Poll https://d23du7ibe4a1ni.cloudfront.net/pending.json every 15 seconds.
2. Read the first queued video ID.
3. Process that video.
4. Send a DELETE request to `/api/pending` with the processed `videoId`.
5. Confirm the pending entry is removed from the local queue state.
