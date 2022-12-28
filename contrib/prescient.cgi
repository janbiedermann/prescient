#!/bin/bash
PD='/var/lib/prescient/' # must have / at the end

# write out header
echo 'Content-Type: text/html'
echo ''
echo '<html><head><title>prescient</title><meta name="color-scheme" content="light dark"/></head>'
echo '<body><h2>Prescient CI Run Results</h2>'
echo '<ul>'

function circle() {
    echo -n "<svg width=\"16\" height=\"16\"><circle cx=\"8\" cy=\"8\" r=\"6\" stroke=\"$1\" fill=\"$1\" /></svg>"
}

function dont_understand() {
    echo "Don't understand query."
}

# parse QUERY_STRING
OIFS="$IFS"
IFS="${IFS}&"
set $QUERY_STRING >/dev/null
qargs="$*"
IFS="$OIFS"

if [ -z "$qargs" ]; then
    # simply list repos
    repos=(`ls -1 "$PD"`)
    for repo in "${repos[@]}"; do
        echo "<li><a href=\"${SCRIPT_NAME}?repo=${repo}\">${repo}</a></li>"
    done
else
    # list sub repo or result
    for arg in $qargs; do
        IFS="${OIFS}="
        set $arg >/dev/null
        IFS="${OIFS}"

        subdir=$2
        echo "<h3>${subdir}</h3>"

        if [[ "$subdir" == *".."* ]]; then # guard
            dont_understand
        elif [ -z "$subdir"]; then # guard
            dont_understand
        else
            if [ "$1" == "repo" ]; then
                repo_path="${PD}${subdir}"
                repos=(`ls -1t "${repo_path}"`)
                for repo in "${repos[@]}"; do
                    rd_path="${repo_path}/${repo}"
                    if [ -d "$rd_path" ]; then
                        echo "<li><a href=\"${SCRIPT_NAME}?repo=${subdir}/${repo}\">${repo}</a></li>"
                    elif [ -f "$rd_path" ]; then
                        errrs=(`grep -o -i -E '[0-9]+ errors' "$rd_path"`)
                        fails=(`grep -o -i -E '[0-9]+ failures' "$rd_path"`)
                        skips=(`grep -o -i -E '[0-9]+ skips' "$rd_path"`)
                        pendg=(`grep -o -i -E '[0-9]+ pending' "$rd_path"`)
                        echo -n '<li>'
                        c=${#errrs[@]}
                        if [ $c -eq 0 ]; then
                            c=${#fails[@]}
                        fi
                        if [ $c -eq 0 ]; then
                            c=${#skips[@]}
                        fi
                        if [ $c -eq 0 ]; then
                            c=${#pendg[@]}
                        fi
                        for ((i=0;i<$c;i+=2)); do
                            color='darkgreen'
                            e=${errrs[$i]}
                            f=${fails[$i]}
                            s=${skips[$i]}
                            p=${pendg[$i]}
                            if [ -n "$e" ] && [ 0 -ne $e ]; then
                                color='darkred'
                            fi
                            if [ -n "$f" ] && [ 0 -ne $f ]; then
                                color='darkred'
                            fi
                            circle $color
                            if [ -n "$s" ] && [ 0 -ne $s ]; then
                                circle 'darkorange'
                            elif [ -n "$p" ] && [ 0 -ne $p ]; then
                                circle 'darkorange'
                            fi
                            echo -n "&nbsp;|&nbsp;"
                        done
                        echo "<a href=\"${SCRIPT_NAME}?file=${subdir}/${repo}\">${repo}</a></li>"
                    fi
                done
            elif [ "$1" == "file" ]; then
                file_path="${PD}${subdir}"
                if [ -f "$file_path" ]; then
                    echo "<pre>"
                    l=0
                    while read -r line; do
                        l=$(($l+1))
                        printf '%6d: ' "$l"
                        echo "$line"
                    done < "$file_path"
                    echo "<pre>"
                else
                    dont_understand
                fi
            else
                dont_understand
            fi
        fi
    done
fi

# write out footer
echo '</ul></body></html>'
