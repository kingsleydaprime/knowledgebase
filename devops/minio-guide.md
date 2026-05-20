# MinIO Self-Hosted Object Storage Guide

**Last Updated:** May 18, 2026
**Author:** Kingsley Ihemelandu
**Status:** Working Installation on Ubuntu/Debian

---

## What is MinIO?

MinIO is a high-performance, self-hosted object storage server that is 100% compatible with the Amazon S3 API. It stores data as **objects** (files + metadata) inside **buckets** (like folders), rather than using a traditional filesystem hierarchy.

It is open source (AGPLv3), written in Go, and designed to be lightweight and fast enough to run on a single machine or scale to a distributed cluster.

### Why use it over just storing files on disk?

- S3-compatible — any library/SDK that works with AWS S3 works with MinIO
- Built-in web console for managing buckets and objects
- Access control via policies and IAM-style users
- Presigned URLs — generate temporary links to files without exposing credentials
- Works as a backend for tools like Nextcloud, Immich, Velero, MLflow, etc.

### Common use cases

- File/media storage for web apps (images, videos, documents)
- AI/ML data lake (store training datasets, model artifacts)
- Backup storage target
- Local S3 replacement during development

---

## Installation (Hetzner Method — What Actually Works)

This is the clean method that avoids the erasure-set issues with multi-drive setups.

### Step 1 — Update system

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install wget -y
```

### Step 2 — Download MinIO binary

```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
sudo mv minio /usr/local/bin/
sudo chmod +x /usr/local/bin/minio
```

### Step 3 — Create a dedicated user

Never run MinIO as root. Create a system user with no login shell:

```bash
sudo useradd -r minio-user -s /sbin/nologin
sudo mkdir /home/minio-user
sudo chown minio-user:minio-user /home/minio-user
```

### Step 4 — Create data directory

```bash
sudo mkdir /data
sudo chown minio-user:minio-user /data
```

### Step 5 — Create systemd service

```bash
sudo nano /etc/systemd/system/minio.service
```

Paste this:

```ini
[Unit]
Description=MinIO
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target

[Service]
User=minio-user
Group=minio-user
EnvironmentFile=-/etc/default/minio
ExecStart=/usr/local/bin/minio server $MINIO_OPTS /data
Restart=always
RestartSec=5
LimitNOFILE=65536
TasksMax=infinity
TimeoutSec=infinity
OOMScoreAdjust=-1000

[Install]
WantedBy=multi-user.target
```

> **Why single `/data` dir instead of `{0...3}`?**
> The `miniodrive{0...3}` erasure-set notation requires MinIO to initialize the drives itself.
> Manually created dirs won't be recognized. For a single machine, just use one path.

### Step 6 — Configure environment variables

```bash
sudo nano /etc/default/minio
```

```bash
MINIO_ROOT_USER=your_strong_username
MINIO_ROOT_PASSWORD=SuperStrongPassword123!@#
MINIO_OPTS="--console-address :9001"
```

> Never leave credentials as `minioadmin/minioadmin` in any environment beyond local testing.

### Step 7 — Start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now minio
sudo systemctl status minio
```

### Access

| Interface  | URL                        |
|------------|----------------------------|
| S3 API     | `http://localhost:9000`    |
| Web Console| `http://localhost:9001`    |

---

## MinIO Client (mc)

`mc` is the CLI tool for interacting with MinIO. More powerful than the web console for scripting and automation.

### Install

```bash
wget https://dl.min.io/client/mc/release/linux-amd64/mc
sudo mv mc /usr/local/bin/
sudo chmod +x /usr/local/bin/mc
```

### Connect to your MinIO instance

```bash
mc alias set local http://localhost:9000 your_root_user your_password
```

### Common commands

```bash
# List buckets
mc ls local

# Create a bucket
mc mb local/my-bucket

# Upload a file
mc cp ./file.txt local/my-bucket/

# Upload a folder recursively
mc cp --recursive ./folder/ local/my-bucket/folder/

# Download a file
mc cp local/my-bucket/file.txt ./

# Delete a file
mc rm local/my-bucket/file.txt

# Generate a presigned URL (valid for 7 days)
mc share download --expire 168h local/my-bucket/file.txt

# Watch bucket activity in real time
mc watch local/my-bucket
```

---

## Using MinIO in Code

### Node.js / TypeScript (minio SDK)

```bash
npm install minio
```

```typescript
import * as Minio from 'minio';

const client = new Minio.Client({
  endPoint: 'localhost',
  port: 9000,
  useSSL: false,
  accessKey: process.env.MINIO_ACCESS_KEY!,
  secretKey: process.env.MINIO_SECRET_KEY!,
});

// Upload a file
await client.fPutObject('my-bucket', 'photo.jpg', '/local/path/photo.jpg', {
  'Content-Type': 'image/jpeg',
});

// Generate a presigned URL (read-only, expires in 24h)
const url = await client.presignedGetObject('my-bucket', 'photo.jpg', 86400);

// Delete an object
await client.removeObject('my-bucket', 'photo.jpg');
```

### Python (boto3 — S3-compatible)

```python
import boto3

client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='your_access_key',
    aws_secret_access_key='your_secret_key',
)

# Upload
client.upload_file('local_file.txt', 'my-bucket', 'remote_file.txt')

# Generate presigned URL
url = client.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'remote_file.txt'},
    ExpiresIn=3600
)

# Download
client.download_file('my-bucket', 'remote_file.txt', 'downloaded.txt')
```

### Best practices when writing code against MinIO

- **Never hardcode credentials** — always use `.env` / environment variables
- **Use presigned URLs** for giving users access to files instead of making buckets public
- **Set Content-Type metadata** when uploading — browsers need it to handle files correctly
- **Catch errors** — MinIO throws on missing buckets, wrong credentials, network issues
- **Reuse the client instance** — don't instantiate a new client per request
- **Use multipart upload** for files over 100MB (the SDK handles this automatically)
- **Set bucket policies** to `private` by default — open only what needs to be open
- **Store only the object key in your DB**, not the full URL — URLs change when you move servers

---

## Security

### Change default credentials immediately

`minioadmin/minioadmin` is publicly known. Set strong credentials in `/etc/default/minio`.

### Create IAM users instead of using root

In the web console: **Identity > Users > Create User**

Assign policies per user. Root credentials should only be used for admin operations.

### Bucket policies

Set via the console or `mc`:

```bash
# Make bucket fully private (default)
mc anonymous set none local/my-bucket

# Make bucket publicly readable (for public assets like avatars)
mc anonymous set download local/public-assets
```

### Enable HTTPS (production)

1. Get a cert (Let's Encrypt via certbot, or self-signed for internal use)
2. Copy cert files:

```bash
sudo mkdir -p /home/minio-user/.minio/certs
sudo cp fullchain.pem /home/minio-user/.minio/certs/public.crt
sudo cp privkey.pem /home/minio-user/.minio/certs/private.key
sudo chown -R minio-user:minio-user /home/minio-user/.minio/
sudo systemctl restart minio
```

3. Update your env file and code to use `useSSL: true` and port `443`.

### Firewall

Only expose ports that need to be exposed:

```bash
# Allow only local access (for apps on the same machine)
sudo ufw deny 9000
sudo ufw deny 9001

# Or allow specific IPs only
sudo ufw allow from 192.168.1.0/24 to any port 9000
```

---

## Debugging

### Service stuck in "activating"

```bash
journalctl -u minio -f
```

This shows real-time logs. The error there is always more descriptive than `systemctl status`.

### Drive not found error

Caused by wrong ownership or wrong path in service file.

```bash
sudo chown -R minio-user:minio-user /data
sudo systemctl restart minio
```

If using erasure sets (`{0...3}`), the dirs must be **completely empty** and created before MinIO first runs — never manually populated.

### Port already in use

```bash
sudo lsof -i :9000
sudo kill -9 <PID>
```

If it keeps respawning, a previous systemd start is still alive:

```bash
sudo systemctl stop minio
sudo killall minio
```

### Console blank / not loading

- Check that `--console-address :9001` is in `MINIO_OPTS`
- Visit `http://localhost:9001` directly (9000 redirects to 9001)
- Check firewall isn't blocking 9001

### Permission denied on /data

```bash
sudo ls -la /data
sudo chown -R minio-user:minio-user /data
```

### Check logs at any time

```bash
journalctl -u minio --since "10 minutes ago"
journalctl -u minio -n 100
```

---

## Updating MinIO

```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /tmp/minio
sudo systemctl stop minio
sudo mv /tmp/minio /usr/local/bin/minio
sudo chmod +x /usr/local/bin/minio
sudo systemctl start minio
```

---

## Upload Architecture — How to Handle File Uploads Properly

This is where most people get it wrong. There are three approaches, and the right one depends on context.

---

### Approach 1: Server Proxies the Upload (Avoid at Scale)

```
Client → POST /upload → Your Server → MinIO
```

Your server receives the entire file, holds it in memory or on disk, then forwards it to MinIO.

**When to use it:**
- You need to validate or transform the file before it's stored (e.g., resize image, strip EXIF data)
- MinIO is on a private network with no external access
- Internal tools with low traffic

**Problems:**
- Your server handles all the bytes — doubles bandwidth usage
- Ties up threads/connections on large files
- Your server becomes the bottleneck
- Memory pressure under concurrent uploads

---

### Approach 2: Presigned URL (Recommended for Most Apps)

```
Client → POST /upload/init → Your Server → (generates URL) → returns URL to Client
Client → PUT file directly → MinIO
Client → POST /upload/complete → Your Server → save object key to DB
```

Your server never touches the file bytes. MinIO receives the upload directly from the client. This is exactly how AWS S3 works in production.

**Why this is correct:**
- Zero load on your server for file transfer
- MinIO handles streaming, chunking, retries
- Scales to any file size without touching your server's memory
- Clean separation — your server handles business logic, MinIO handles storage

**Step-by-step flow:**

1. Client requests an upload URL:
   ```
   POST /upload/init
   Body: { filename: "photo.jpg", contentType: "image/jpeg", size: 204800 }
   ```

2. Your server validates auth, checks file type/size, generates a presigned PUT URL:
   ```typescript
   // NestJS / Express handler
   async getUploadUrl(filename: string, contentType: string) {
     const objectKey = `uploads/${Date.now()}-${filename}`;
     
     const url = await this.minioClient.presignedPutObject(
       'my-bucket',
       objectKey,
       60 * 15 // expires in 15 minutes
     );
     
     return { uploadUrl: url, objectKey };
   }
   ```

3. Server returns `{ uploadUrl, objectKey }` to client

4. Client uploads directly to MinIO:
   ```typescript
   // Frontend
   await fetch(uploadUrl, {
     method: 'PUT',
     body: file,
     headers: { 'Content-Type': file.type },
   });
   ```

5. Client notifies server the upload is complete:
   ```
   POST /upload/complete
   Body: { objectKey: "uploads/1234567890-photo.jpg" }
   ```

6. Server saves `objectKey` to DB (not the full URL — see best practices below)

---

### Approach 3: Dedicated Upload Service (Overkill for Most)

Only worth building if uploads are a core product feature — think YouTube, Cloudinary, or a document processing platform. For a standard app with file attachments, Approach 2 is enough.

---

### Where Queues Come In (Post-Upload Processing)

Queues are not for the upload itself — they are for everything that happens **after** the file lands in MinIO.

Examples of async post-processing:
- Generate thumbnails or multiple image sizes
- Transcode video to different formats
- Run a virus/malware scan
- Extract metadata (EXIF, document text, etc.)
- Send a notification email ("Your file has been processed")
- Index content for search

**Flow with a queue:**

```
Upload completes
    → Client calls POST /upload/complete
    → Server saves objectKey to DB (status: "processing")
    → Server pushes job to queue (RabbitMQ / BullMQ)
    → Worker picks up job, processes file
    → Worker updates DB (status: "ready")
    → (Optional) Worker emits event / sends webhook to notify client
```

Never do heavy processing synchronously inside the upload response. A user should not wait 10 seconds for a response because your server is transcoding video.

**BullMQ example (Node.js):**

```typescript
// Producer — in your upload complete handler
await uploadQueue.add('process-image', {
  objectKey: 'uploads/1234567890-photo.jpg',
  userId: user.id,
});

// Worker
uploadQueue.process('process-image', async (job) => {
  const { objectKey, userId } = job.data;
  // download from MinIO, generate thumbnail, re-upload
});
```

---

### File Validation — Where and What

**Never trust the client.** Validate on both sides.

| What to validate | Where |
|---|---|
| File size limit | Client (UX) + Server (security) |
| Allowed MIME types | Client (UX) + Server (security) |
| Actual file content (magic bytes) | Server or worker |
| Malware | Worker (async, post-upload) |

**Never validate by file extension alone.** A `.jpg` file can contain anything. Check the actual magic bytes:

```typescript
// Using the 'file-type' package
import { fileTypeFromBuffer } from 'file-type';

const buffer = await file.arrayBuffer();
const type = await fileTypeFromBuffer(buffer);

if (!['image/jpeg', 'image/png', 'image/webp'].includes(type?.mime)) {
  throw new BadRequestException('Invalid file type');
}
```

**Server-side size enforcement on presigned URLs:**

MinIO doesn't natively enforce size on presigned PUT URLs, so validate size before generating the URL:

```typescript
const MAX_SIZE = 10 * 1024 * 1024; // 10MB
if (fileSize > MAX_SIZE) throw new BadRequestException('File too large');
```

---

### Object Key Strategy (How to Name Files in MinIO)

Bad: saving the original filename as-is
- Collisions between users
- Path traversal risk
- Spaces and special characters break URLs

Good pattern:

```
{scope}/{userId}/{timestamp}-{uuid}.{ext}
```

Examples:
```
avatars/user_abc123/1716038400-f47ac10b.jpg
documents/user_abc123/1716038400-3e4d5f6a.pdf
posts/post_xyz/cover-1716038400.webp
```

**Store only the object key in your DB, not the full URL.** URLs change when you move servers, change domains, or switch from HTTP to HTTPS. Reconstruct the URL at read time:

```typescript
// Stored in DB: "avatars/user_abc123/1716038400-f47ac10b.jpg"
// At read time:
const url = await minioClient.presignedGetObject('my-bucket', objectKey, 3600);
```

---

### Summary — Decision Table

| Scenario | Approach |
|---|---|
| Simple internal tool | Server proxy (Approach 1) |
| Need to validate/transform before storing | Server proxy (Approach 1) |
| Standard app with user file uploads | Presigned URL (Approach 2) |
| High traffic / large files | Presigned URL (Approach 2) |
| Post-upload processing (thumbnails, transcoding) | Presigned URL + Queue |
| Uploads are the core product feature | Dedicated upload service (Approach 3) |

---

## Useful References

- Official docs: https://min.io/docs/minio/linux/index.html
- mc reference: https://min.io/docs/minio/linux/reference/minio-mc.html
- Node.js SDK: https://min.io/docs/minio/linux/developers/javascript/minio-javascript.html
- Hetzner tutorial (what worked): https://community.hetzner.com/tutorials/how-to-install-minio-on-debian
