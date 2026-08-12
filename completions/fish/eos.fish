# Fish completion for repository-local EOS.
function __eos_dynamic_complete
    set -l tokens (commandline -opc)
    set -l current (commandline -ct)
    if test (count $tokens) -eq 0
        return
    end
    set -l cmd $tokens[1]
    set -e tokens[1]
    command $cmd completion candidates -- $tokens $current 2>/dev/null
end
complete -c eos -f -a '(__eos_dynamic_complete)'
