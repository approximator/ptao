workflow "apms" {
  on = "push"
  resolves = ["Build"]
}

action "Build" {
  uses = "./.github/apmsui-build"
}
