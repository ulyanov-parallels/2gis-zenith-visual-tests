package Autotests5.vcsRoots

import jetbrains.buildServer.configs.kotlin.v10.*
import jetbrains.buildServer.configs.kotlin.v10.vcs.GitVcsRoot

object Autotests5_GitLab : GitVcsRoot({
    uuid = "777858f4-a28e-40fc-ad48-e07c99da0efa"
    extId = "Autotests5_GitLab"
    name = "GitLab_zenith_visual"
    url = "https://gitlab.2gis.ru/zenith_autotests/zenith_visual.git"
    branchSpec = "+:refs/heads/*"
    authMethod = password {
        userName = "v.ulyanov"
        password = "zxx525c7c646dfce242d2cb9dde0b625cb77ac8bca679e17d6ff888e94fbb4b371841d40a4823526713"
    }
})
