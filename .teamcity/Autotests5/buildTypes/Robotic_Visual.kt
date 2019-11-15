package Autotests5.buildTypes

import jetbrains.buildServer.configs.kotlin.v10.*
import jetbrains.buildServer.configs.kotlin.v10.BuildFeature
import jetbrains.buildServer.configs.kotlin.v10.BuildFeature.*
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.ScriptBuildStep
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.ScriptBuildStep.*
import jetbrains.buildServer.configs.kotlin.v10.buildSteps.script
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.BuildFailureOnText
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.BuildFailureOnText.*
import jetbrains.buildServer.configs.kotlin.v10.failureConditions.failOnText

object Robotic_Visual : BuildType({
    uuid = "777ec191-acb3-4607-ab97-57399ded0a9a"
    extId = "Robotic_Visual"
    name = "Robotic_Visual"
    description = "Visual tests execution"

    allowExternalStatus = true
    artifactRules = "%env.RESULTS%"

    params {
        text("01_build", "%dep.Autotests5_Niffler.01_build%", label = "Build number", description = "BenchmarkBatch buiild number", allowEmpty = false)
        select("02_device", "", label = "Device",
                options = listOf("Asus_ZenFone_2", "Lenovo_K3_Note", "Lenovo_Yoga_Tablet_2", "LG_Nexus5", "Nokia_6", "Samsung_Galaxy_S4", "Samsung_Galaxy_A5", "Samsung_Galaxy_SIII", "Sony_Xperia_S", "Sony_Xperia_M5"))
        select("03_test", "", label = "Test", description = "test name",
                options = listOf("moscow1"))
    }

    vcs {
        root(Autotests5.vcsRoots.Autotests5_GitLab)

        checkoutMode = CheckoutMode.ON_SERVER
    }

    steps {
        script {
            name = "Main"
            scriptContent = "deactivate && activate %env.PYTHON_ENV% && python %env.PROJECT_DIR%/main.py"
        }
    }

    failureConditions {
        errorMessage = true
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

    features {
        feature {
            type = "allureTeamCityPlugin.buildFeature"
            enabled = false
            param("allureTeamCityPlugin.reportVersion", "1.4.0")
            param("allureTeamCityPlugin.resultsPattern", "%env.ALLURE_HOME%")
        }
    }

    dependencies {
        dependency(Autotests5.buildTypes.Autotests5_Niffler) {
            snapshot {
                reuseBuilds = ReuseBuilds.NO
                onDependencyFailure = FailureAction.CANCEL
                onDependencyCancel = FailureAction.CANCEL
            }
        }
    }

    cleanup {
        all(days = 100)
        history(days = 100)
        artifacts(days = 100)
    }
    
    disableSettings("RUNNER_15")
})
