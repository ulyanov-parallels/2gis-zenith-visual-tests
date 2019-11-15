package Autotests5

import Autotests5.buildTypes.*
import Autotests5.vcsRoots.*
import Autotests5.vcsRoots.Autotests5_GitLab
import jetbrains.buildServer.configs.kotlin.v10.*
import jetbrains.buildServer.configs.kotlin.v10.Project
import jetbrains.buildServer.configs.kotlin.v10.ProjectFeature
import jetbrains.buildServer.configs.kotlin.v10.ProjectFeature.*
import jetbrains.buildServer.configs.kotlin.v10.projectFeatures.VersionedSettings
import jetbrains.buildServer.configs.kotlin.v10.projectFeatures.VersionedSettings.*
import jetbrains.buildServer.configs.kotlin.v10.projectFeatures.versionedSettings

object Project : Project({
    uuid = "777b7548-b6a9-442f-9dc8-54e2ce1beab0"
    extId = "Autotests5"
    parentId = "_Root"
    name = "Autotests5"
    description = "Zenith Visual"

    vcsRoot(Autotests5_GitLab)

    buildType(Autotests5_Niffler)
    buildType(Robotic_Visual)

    params {
        param("env.CHECKOUT_DIR", "%teamcity.build.checkoutDir%")
        param("env.DATA", """%env.CHECKOUT_DIR%\data""")
        param("env.PROJECT_DIR", """%env.CHECKOUT_DIR%\project""")
        param("env.PROJECT_NAME", "zenith_visual")
        param("env.PYTHON_ENV", "%env.PROJECT_NAME%_env")
        param("env.PYTHON_INTERPRETER", """C:\Anaconda2\python.exe""")
        param("env.RESULTS", """%env.CHECKOUT_DIR%\results""")
        param("env.SCRIPTS", """%env.CHECKOUT_DIR%\scripts""")
    }

    features {
        feature {
            id = "PROJECT_EXT_1"
            type = "project-graphs"
            param("series", """
                [
                  {
                    "type": "valueType",
                    "title": "Success Rate",
                    "sourceBuildTypeId": "Autotests3_1TilesZenith",
                    "key": "SuccessRate"
                  },
                  {
                    "type": "valueType",
                    "title": "BuildTestStatus",
                    "sourceBuildTypeId": "Autotests3_1TilesZenith",
                    "key": "BuildTestStatus"
                  }
                ]
            """.trimIndent())
            param("format", "percent")
            param("hideFilters", "")
            param("title", "New chart title")
            param("defaultFilters", "")
            param("seriesTitle", "Serie")
        }
        feature {
            id = "PROJECT_EXT_2"
            type = "project-graphs.order"
            param("order", "PROJECT_EXT_1")
        }
        versionedSettings {
            id = "PROJECT_EXT_3"
            mode = VersionedSettings.Mode.ENABLED
            buildSettingsMode = VersionedSettings.BuildSettingsMode.PREFER_CURRENT_SETTINGS
            rootExtId = Autotests5_GitLab.extId
            showChanges = false
            settingsFormat = VersionedSettings.Format.KOTLIN
        }
    }
    buildTypesOrder = arrayListOf(Autotests5.buildTypes.Autotests5_Niffler, Autotests5.buildTypes.Robotic_Visual)
})
