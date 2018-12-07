# gpu-passthrough-vm
Rpmbuild for a Windows 10 VM for Fedora

Command: 
cd <git_cloned_repo_dir>
rpmbuild --define "_topdir $PWD" -bb SPECS/gpu-passthrough-vm.spec
