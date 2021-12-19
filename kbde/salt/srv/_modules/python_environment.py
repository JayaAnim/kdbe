

def exists(python_version):
    __salt__["state.apply"]("python_repo")
