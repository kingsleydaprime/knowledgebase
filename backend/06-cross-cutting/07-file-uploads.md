# File Uploads

> **[Intermediate]** · The gap the old README named — and the one feature where nearly every naive implementation is a vulnerability.

**File upload is where untrusted input meets your filesystem, your storage bill, and your image library's parser.** It deserves its own note because the naive version is wrong in about six independent ways.

## Don't proxy the bytes through your API

**The single most important architectural decision here.**

The obvious design — client uploads to your server, your server writes to storage — makes your API a bottleneck: it ties up a request thread for the whole upload, consumes memory or disk, and scales badly.

**Use a presigned URL instead:**

```
1. client → your API: "I want to upload profile.jpg, 2 MB, image/jpeg"
2. your API: authorise, validate the claim, generate a presigned PUT URL (5 min expiry)
3. client → object storage directly: PUT the bytes
4. client → your API: "done, here's the key"
5. your API: verify the object exists, check its real size and type, record it
```

**Your server never touches the bytes.** It authorises, and it verifies afterwards → [[devops/03-cloud/03-object-storage-and-direct-uploads|object storage and direct uploads]].

**Step 5 is not optional.** Between steps 2 and 4 the client controls what was actually uploaded — so re-check size and content type from storage metadata, never from what the client told you.

## Validation, and why the obvious checks don't work

**The extension means nothing.** `evil.php.jpg`, `shell.jpg` containing PHP — the filename is client-supplied text.

**The `Content-Type` header means nothing.** Also client-supplied.

**Check the magic bytes** — the file's actual signature (`\xFF\xD8\xFF` for JPEG, `\x89PNG` for PNG) — and **allowlist** the types you accept. Never denylist.

**Then re-encode.** For images, decoding and re-encoding server-side strips embedded payloads, EXIF (which contains GPS coordinates — a genuine privacy leak) and polyglot tricks. **It also normalises the format**, which is worth it on its own.

**Enforce size limits at every layer** — proxy, framework, and storage policy. **The presigned URL should carry a content-length condition**, or a client can upload 5 GB to a URL you issued for 2 MB.

**Limit dimensions, not just bytes.** A **decompression bomb** — a 10 KB PNG that decodes to 50,000×50,000 pixels — exhausts memory when your image library opens it. Check declared dimensions *before* decoding.

## Storing them

**Never write to a path derived from the user's filename.** `../../etc/cron.d/x` is path traversal; a Windows reserved name like `CON` breaks differently.

**Generate your own key:**

```
uploads/{tenant}/{uuid}.{validated-extension}
```

Store the original filename as **metadata**, and escape it when displaying it.

**Never serve uploads from a directory your web server will execute.** The classic RCE is uploading a `.php` (or `.jsp`, `.aspx`) file into a served directory. **Object storage sidesteps this entirely**, which is another argument for it.

**Serve from a different origin** — `usercontent.example.com`, not your app's domain. A stored HTML or SVG file executing on your origin has access to your cookies and your DOM. **SVG is an XSS vector** — it can contain `<script>` — so either serve it with `Content-Disposition: attachment`, sanitise it, or don't accept it.

**Always set `Content-Type` explicitly on retrieval** and `X-Content-Type-Options: nosniff` → [[backend/06-cross-cutting/06-security-headers-and-cors|note 06]].

## Large files

**Multipart / chunked upload** — split into parts, upload independently, storage reassembles. Gives you resumability, parallelism, and no single enormous request.

**Resumable protocols** — [tus](https://tus.io) is the open standard; S3 and friends have their own multipart APIs.

**Track upload state** so a client can resume. And **expire abandoned uploads** — incomplete multipart uploads are billed and invisible in the bucket listing, which is a genuinely common surprise on a cloud bill.

## After the upload

**Process asynchronously.** Thumbnailing, transcoding and virus scanning belong in a background job, not the request → [[architecture/02-building-blocks/04-messaging-and-async|messaging and async]].

**Scan for malware** if users can download each other's files. ClamAV is the usual starting point.

**Decide the deletion story before you build.** Orphaned objects — the database row was rolled back but the object was written — accumulate forever. **Reconcile periodically**, and remember that "delete the user" now means deleting their objects too, which is a GDPR obligation as much as a tidiness one → [[cybersecurity/08-governance-risk-and-compliance/README|GRC]].

## The checklist

- [ ] Direct-to-storage with a presigned URL, not proxied
- [ ] Authorise **before** issuing the URL; verify **after** the upload
- [ ] Allowlist content types by **magic bytes**, not extension or header
- [ ] Size limits at proxy, app **and** in the presigned policy
- [ ] Dimension limits before decoding
- [ ] Re-encode images; strip EXIF
- [ ] Server-generated storage keys; original filename as metadata only
- [ ] Serve from a separate origin, `nosniff`, explicit `Content-Type`
- [ ] SVG handled deliberately
- [ ] Async post-processing; abandoned uploads expired
- [ ] A deletion and reconciliation story

## Related
- [[devops/03-cloud/03-object-storage-and-direct-uploads|object storage and direct uploads]]
- [[backend/06-cross-cutting/06-security-headers-and-cors|security headers]]
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]]

*Source: [reference] — written Aug 2026, closing the gap the previous README named as "not covered anywhere yet".*
