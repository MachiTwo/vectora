def filesInScope(List<String> files, String prefix) {
  return files.any { it == prefix || it.startsWith(prefix) }
}

def changedFileList(String rawFiles) {
  return rawFiles?.trim() ? rawFiles.readLines().findAll { it?.trim() } : []
}

pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    skipDefaultCheckout(true)
  }

  environment {
    PRE_COMMIT_HOME = "${WORKSPACE}/.cache/pre-commit"
    PIP_CACHE_DIR = "${WORKSPACE}/.cache/pip"
    NPM_CONFIG_CACHE = "${WORKSPACE}/.cache/npm"
    GOMODCACHE = "${WORKSPACE}/.cache/go"
    GOFLAGS = "-mod=mod"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git fetch --tags --force --prune'
      }
    }

    stage('Prepare') {
      steps {
        script {
          env.IS_TAG_BUILD = (env.TAG_NAME?.trim()?.startsWith('v') ? 'true' : 'false')
          env.RUN_ALL = env.IS_TAG_BUILD

          if (env.IS_TAG_BUILD == 'true') {
            def rawVersion = env.TAG_NAME.trim().substring(1)
            env.VECTORA_VERSION = rawVersion
            env.VECTORA_CHANNEL = rawVersion.endsWith('.dev') ? 'dev' : 'stable'
          } else {
            def shortSha = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
            env.VECTORA_VERSION = "0.0.0.dev+${shortSha}"
            env.VECTORA_CHANNEL = 'dev'
          }
          env.DOCKER_TAG = env.VECTORA_VERSION.replaceAll('[^A-Za-z0-9_.-]', '-')

          def rawChangedFiles = sh(
            script: '''
              set -e
              parent="$(git rev-parse HEAD^ 2>/dev/null || true)"
              if [ -n "$parent" ]; then
                git diff --name-only "$parent" HEAD
              else
                git ls-files
              fi
            ''',
            returnStdout: true
          ).trim()

          env.CHANGED_FILES = rawChangedFiles
          if (env.RUN_ALL == 'true') {
            env.CHANGED_FILES = sh(script: 'git ls-files', returnStdout: true).trim()
          }

          echo "Version: ${env.VECTORA_VERSION}"
          echo "Channel: ${env.VECTORA_CHANNEL}"
          echo "Run all files: ${env.RUN_ALL}"
        }
      }
    }

    stage('Pre-commit') {
      steps {
        script {
          if (env.RUN_ALL == 'true') {
            sh 'pre-commit run --all-files'
            return
          }

          def changedFiles = env.CHANGED_FILES?.trim() ? env.CHANGED_FILES.readLines().findAll { it?.trim() } : []
          if (changedFiles.isEmpty()) {
            echo 'No changed files detected. Skipping pre-commit.'
            return
          }

          writeFile file: '.ci-changed-files', text: changedFiles.join('\n') + '\n'
          sh '''
            python3 - <<'PY'
from pathlib import Path
import subprocess

files = [line.strip() for line in Path('.ci-changed-files').read_text().splitlines() if line.strip()]
if not files:
    raise SystemExit(0)

subprocess.run(['pre-commit', 'run', '--files', *files], check=True)
PY
          '''
        }
      }
    }

    stage('Validate Vectora') {
      steps {
        script {
          if (env.RUN_ALL != 'true' && !filesInScope(env.CHANGED_FILES.readLines().findAll { it?.trim() }, 'vectora/')) {
            echo 'No Vectora files changed. Skipping.'
            return
          }

          if (fileExists('vectora/go.mod')) {
            dir('vectora') {
              sh 'go test ./...'
              sh 'go build ./...'
            }
          } else {
            echo 'vectora/go.mod not found. Skipping Go validation for Vectora.'
          }

          if (fileExists('vectora/package.json')) {
            dir('vectora') {
              sh 'npm ci'
              sh 'npm test'
              sh 'npm run build'
            }
          }
        }
      }
    }

    stage('Validate Asset Library') {
      steps {
        script {
          def scopeFiles = env.CHANGED_FILES.readLines().findAll { it?.trim() }
          if (env.RUN_ALL != 'true' && !filesInScope(scopeFiles, 'vectora-asset-library/')) {
            echo 'No asset library files changed. Skipping.'
            return
          }

          if (!fileExists('vectora-asset-library/REDME.md')) {
            error 'vectora-asset-library/REDME.md is missing.'
          }

          sh 'test -s vectora-asset-library/REDME.md'
        }
      }
    }

    stage('Validate Cognitive Runtime') {
      steps {
        script {
          def scopeFiles = env.CHANGED_FILES.readLines().findAll { it?.trim() }
          def touchesRuntime = filesInScope(scopeFiles, 'vectora-cognitive-runtime/') || filesInScope(scopeFiles, 'scripts/')
          if (env.RUN_ALL != 'true' && !touchesRuntime) {
            echo 'No cognitive runtime or script files changed. Skipping.'
            return
          }

          def pythonFiles = sh(
            script: "git ls-files 'vectora-cognitive-runtime/**/*.py' 'scripts/**/*.py'",
            returnStdout: true
          ).trim()

          if (pythonFiles) {
            sh '''
              python3 - <<'PY'
import py_compile
from pathlib import Path

paths = []
for root in (Path('vectora-cognitive-runtime'), Path('scripts')):
    if root.exists():
        paths.extend(root.rglob('*.py'))

for path in paths:
    py_compile.compile(str(path), doraise=True)
PY
            '''
          } else {
            echo 'No Python files found for cognitive runtime validation.'
          }
        }
      }
    }

    stage('Validate Integrations') {
      steps {
        script {
          def scopeFiles = env.CHANGED_FILES.readLines().findAll { it?.trim() }
          if (env.RUN_ALL != 'true' && !filesInScope(scopeFiles, 'vectora-integrations/')) {
            echo 'No integrations files changed. Skipping.'
            return
          }

          if (fileExists('vectora-integrations/package.json')) {
            dir('vectora-integrations') {
              sh 'npm ci'
              sh 'npm test'
              sh 'npm run build'
            }
          } else {
            echo 'vectora-integrations/package.json not found. Skipping Node validation.'
          }
        }
      }
    }

    stage('Validate Website') {
      steps {
        script {
          def scopeFiles = env.CHANGED_FILES.readLines().findAll { it?.trim() }
          if (env.RUN_ALL != 'true' && !filesInScope(scopeFiles, 'vectora-website/')) {
            echo 'No website files changed. Skipping.'
            return
          }

          dir('vectora-website') {
            sh 'python3 build_local.py'
          }
        }
      }
    }

    stage('Build Docker Images') {
      steps {
        script {
          def scopeFiles = changedFileList(env.CHANGED_FILES)
          def touchesDockerSources = env.RUN_ALL == 'true' || !scopeFiles.isEmpty()

          if (!touchesDockerSources) {
            echo 'No Docker-scoped files changed. Skipping image builds.'
            return
          }

          sh "docker build -t vectora/vectora:${env.DOCKER_TAG} vectora"
          sh "docker build -t vectora/asset-library:${env.DOCKER_TAG} vectora-asset-library"
          sh "docker build -t vectora/cognitive-runtime:${env.DOCKER_TAG} vectora-cognitive-runtime"
          sh "docker build -t vectora/monorepo:${env.DOCKER_TAG} ."
        }
      }
    }

    stage('Deploy Hook') {
      when {
        expression { return env.IS_TAG_BUILD == 'true' }
      }
      steps {
        script {
          if (env.VECTORA_CHANNEL == 'dev') {
            echo "Dev tag detected (${env.VECTORA_VERSION}). This is the place to publish a dev image or restart a dev stack on the VPS."
          } else {
            echo "Stable tag detected (${env.VECTORA_VERSION}). This is the place to deploy production containers on the VPS."
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '.ci-changed-files', allowEmptyArchive: true
      cleanWs(deleteDirs: true, disableDeferredWipeout: true)
    }
  }
}
