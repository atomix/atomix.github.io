// SPDX-FileCopyrightText: 2022-present Intel Corporation
//
// SPDX-License-Identifier: Apache-2.0

function showLanguageGo() {
    document.getElementById("atx-spotlight__code-golang").style.display = "block";
    document.getElementById("atx-spotlight__language-golang").classList.add("atx-spotlight__language-selected");
    document.getElementById("atx-spotlight__code-java").style.display = "none";
    document.getElementById("atx-spotlight__language-java").classList.remove("atx-spotlight__language-selected");
}

function showLanguageJava() {
    document.getElementById("atx-spotlight__code-java").style.display = "block";
    document.getElementById("atx-spotlight__language-java").classList.add("atx-spotlight__language-selected");
    document.getElementById("atx-spotlight__code-golang").style.display = "none";
    document.getElementById("atx-spotlight__language-golang").classList.remove("atx-spotlight__language-selected");
}
