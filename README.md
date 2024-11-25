## User API

Testing some DevOps skills

### How to upload and retreive a profile picture
```bash
curl -v -u <username>:<password> -X POST -F "profile_picture=@/home/apiyo/gitrepos/onadata/profile.jpeg" http://127.0.0.1:8000/user-profile/

curl -v -u <username>:<password> http://127.0.0.1:8000/user-profile/
```

### Run minio locally
```bash
docker run  -p 9000:9000 -p 9001:9001 \
 quay.io/minio/minio server /data --console-address ":9001"
```
