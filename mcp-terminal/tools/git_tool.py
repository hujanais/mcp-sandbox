from git import Repo

if __name__ == '__main__':

    repo_url = "git@gitlab.morsecorp.com:maven/infrastructure/hyperion.git"
    # repo = Repo.clone_from(repo_url, "local_dir")
    repo = Repo('/Users/tlee/projects/themis/webui-frontend')

    main_commit = repo.commit('HEAD')
    sha_commit = repo.commit('HEAD~1')
    # patch_text = repo.git.diff("head", sha)
    diff_index = sha_commit.diff(main_commit, create_patch=True)

    for diff_item in diff_index:
        print(f"Change Type: {diff_item.change_type} {diff_item.a_path} -> {diff_item.b_path}")
        print('show', diff_item.diff.decode('utf-8'))
        print('-----------------------')
        break
