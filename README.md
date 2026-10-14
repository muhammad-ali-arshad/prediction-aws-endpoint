# Linear regression API — FA23-BDS-024---

The supplied Flask API uses seed `24`, generates `a1`, `a2`, `a3`, and `b`
using the lab's fixed `random.seed` / `random.uniform` procedure, and returns
`round(a1*x1 + a2*x2 + a3*x3 + b, 2)` as JSON.

The API listens on **5500 inside the container**. Docker Compose publishes
**5500 on the EC2 host**, as requested. Gunicorn serves the app.

The lab handout specifies public port **5000**. This configuration uses **5500**;
confirm the evaluator will use that port before submission.

```text
GitHub push → Jenkins webhook → EC2 agent → build image → push Docker Hub
            → docker compose up → verify prediction on localhost:5500
```

## 1. Prepare the EC2 Jenkins agent

Use a Linux Jenkins agent on the **same EC2 host that exposes the API**.
Give that node the label `ec2-docker`. If Jenkins runs directly on that EC2
instance, its node can use this label; if Jenkins is in a container, attach a
host agent so the pipeline uses the EC2 Docker daemon and published ports.

Install Git, Python 3, Docker Engine, and the Docker Compose v2 plugin.
The Jenkins agent's OS user must be allowed to use Docker. For an agent
running as `jenkins`:

```bash
sudo usermod -aG docker jenkins
# Restart the Jenkins service or reconnect the agent for group changes.
```

Check as the agent user:

```bash
git --version
python3 --version
docker info
docker compose version
```

Use Compose v2 with `up --wait` support. Allow inbound TCP **5500** in the
EC2 security group for the instructor's API calls. Jenkins' webhook URL
must also be reachable from GitHub (for example, port 8081 if that is where
your Jenkins server is exposed). The Jenkins agent needs outbound access to
GitHub, Docker Hub, and PyPI.

## 2. Set up Docker Hub and Jenkins

1. Create the Docker Hub repository `prediction-aws-endpoint` under your
   Docker Hub account. Use public visibility if the instructor must pull it.
2. In Jenkins, install the **Pipeline**, **Git**, **GitHub**, and
   **Credentials Binding** plugins.
3. Add a **Username with password** credential with ID **`dockerhub`**.
   Username: your Docker Hub username. Password: a Docker Hub access token
   with permission to push images. Keep the token in Jenkins only.
4. Create a regular **Pipeline** job, e.g. `prediction-aws-endpoint`.
   Set **Definition → Pipeline script from SCM**, SCM **Git**, repository:
   `https://github.com/muhammad-ali-arshad/prediction-aws-endpoint.git`.
   Use branch `*/main` and script path `Jenkinsfile`. If the GitHub repository
   is private, supply a GitHub checkout credential too.
5. Enable **GitHub hook trigger for GITScm polling** in the job configuration.
   The Jenkinsfile also declares `githubPush()`.
6. Run **Build Now** once to register the pipeline trigger, build/push the
   first image, warm the build cache, and confirm the API works.

The Docker Hub image name is:

```text
YOUR_DOCKERHUB_USERNAME/prediction-aws-endpoint:latest
```

The Build stage builds with Compose, authenticates with the saved credential,
pushes the image, and runs:

```bash
docker compose up -d --no-build --force-recreate --wait --wait-timeout 60 api
```

The next stage verifies the registration number, three numerical predictions,
and HTTP 400 for invalid numeric input through host port 5500. Build failures
show the container logs. Successful jobs leave the service running.

## 3. Configure the GitHub webhook

In GitHub repository **Settings → Webhooks → Add webhook**:

- Payload URL: `http://JENKINS_PUBLIC_IP:8081/github-webhook/`
  (use your actual Jenkins base URL and keep the trailing slash).
- Content type: `application/json`.
- Events: **Just the push event**.
- Active: enabled.

Use a matching webhook secret if you configure one in Jenkins. Check the
webhook's recent delivery status and confirm an actual new commit triggers
the job. Jenkins must be running and the `ec2-docker` node must be online.

Reference: [Jenkins GitHub plugin webhook setup](https://plugins.jenkins.io/github/).

## 4. Manually take the API down before evaluation

On the EC2 host, clone this repository (or use the Jenkins job workspace):

```bash
git clone https://github.com/muhammad-ali-arshad/prediction-aws-endpoint.git
cd prediction-aws-endpoint
export DOCKERHUB_USERNAME=YOUR_DOCKERHUB_USERNAME
export IMAGE_TAG=latest
docker compose down
docker compose ps
```

The Compose project name is fixed to `prediction-aws-endpoint`, so `down`
targets the same deployment even from a separate clone on the same Docker
daemon. `restart: "no"` keeps a stopped container from restarting by itself.
There is no scheduled Jenkins trigger.

Confirm the API is unreachable **from another computer**:

```bash
curl --max-time 5 'http://EC2_PUBLIC_IP:5500/predict?x1=2&x2=3&x3=1'
```

Leave it down. A new GitHub push will run the pipeline and start it again.
Do not stop Jenkins or the Docker daemon, and do not disable the webhook.
Do one full rehearsal: take it down, push a small README change, wait for
Jenkins success, and verify the public endpoint. Then take it down again
before the instructor evaluates it. Cached builds help meet the three-minute
check, but confirm that timing on your actual EC2 instance.

## 5. Test the public endpoint

```bash
curl 'http://EC2_PUBLIC_IP:5500/predict?x1=2&x2=3&x3=1'
python3 scripts/verify_api.py http://EC2_PUBLIC_IP:5500
```

Expected response for `(2, 3, 1)`:

```json
{"registration number": "FA23-BDS-024", "prediction": 21.23}
```

## Manual Docker commands

For commands outside Jenkins, copy `.env.example` to `.env` and replace the
username. Alternatively export `DOCKERHUB_USERNAME` as above.

```bash
docker login --username YOUR_DOCKERHUB_USERNAME
docker compose build api
docker compose push api
docker compose up -d --no-build --wait api
docker compose down
```

Reference: [Docker Compose up options](https://docs.docker.com/reference/cli/docker/compose/up/).

## Evaluation access and submission

In GitHub repository **Settings → Collaborators → Add people**, invite the
instructor using `qasimalik@gmail.com` or their confirmed GitHub account.
Ensure they accept the invitation and have write access before evaluation.
Keep `main` pushable by the instructor so their commit triggers Jenkins.
The evaluator also needs whatever Jenkins job read/API access your instructor
requests; a working GitHub webhook alone does not grant Jenkins REST access.

Submit your repository URL, EC2 public IP, and Docker Hub image name with tag
using the [lab submission form](https://forms.gle/wVcBhjFMZvRjefRB6).
The [response sheet](https://docs.google.com/spreadsheets/d/1QZY1xlHVxyw5qI-fNDv5soAYfwH4y3uJAh5BtJN4QvU/)
is supplied by the lab for checking your submission.

Repository files do not configure your EC2 instance, Jenkins credentials/job,
GitHub webhook, collaborator invitation, or form submission automatically.
