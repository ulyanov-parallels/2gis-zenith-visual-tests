package Autotests5.buildTypes

import jetbrains.buildServer.configs.kotlin.v10.*
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.ScriptBuildStep
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.ScriptBuildStep.*
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.script
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.BuildFailureOnText
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.BuildFailureOnText.*
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.failOnText

object Autotests5_Niffler : BuildType({
    uuid = "5f39a4eb-a25c-459f-a5d8-6a0aa082e62c"
    extId = "Autotests5_Niffler"
    name = "Niffler"
    description = "BenchmarkBatch artifacts getter"

    artifactRules = """temp\artifact_link.url"""

    params {
        text("01_build", "", label = "Build number", allowEmpty = false)
    }

    vcs {
        root(Autotests5.vcsRoots.Autotests5_GitLab)

    }

    steps {
        script {
            name = "Setup"
            enabled = false
            executionMode = BuildStep.ExecutionMode.ALWAYS
            scriptContent = """%env.SCRIPTS%\setup\python_env_creation.bat %env.PYTHON_ENV%"""
        }
        script {
            name = "Main"
            scriptContent = "deactivate && activate %env.PYTHON_ENV% && python %env.PROJECT_DIR%/niffler.py -b %01_build%"
        }
    }

    failureConditions {
        failOnText {
            conditionType = BuildFailureOnText.ConditionType.CONTAINS
            pattern = "Exception"
            failureMessage = "Exception:"
            reverse = false
        }
        failOnText {
            conditionType = BuildFailureOnText.ConditionType.CONTAINS
            pattern = "Error"
            failureMessage = "Error:"
            reverse = false
        }
    }
})
