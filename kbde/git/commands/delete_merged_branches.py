from kbde.kbde_cli import command

import os


class Command(command.Command):
    protected_branch_prefixes = [
        "master",
        "dev",
        "stag",
        "prod",
    ]
    current_branch_prefix = "*"
    
    def handle(self):
        import git

        repo = git.Repo(os.getcwd())

        merged_branches = repo.git.branch("--merged")
        merged_branches = merged_branches.split("\n")
        merged_branches = [branch.strip() for branch in merged_branches]

        protected_branch_prefixes = self.get_protected_branch_prefixes()

        for branch in merged_branches:
            if any(
                branch.startswith(prefix)
                for prefix in protected_branch_prefixes
            ):
                continue

            # Try to delete the branch
            try:
                repo.git.branch("-d", branch)
            except git.exc.GitCommandError as e:
                pass

    def get_protected_branch_prefixes(self):
        return [self.current_branch_prefix] + self.protected_branch_prefixes
