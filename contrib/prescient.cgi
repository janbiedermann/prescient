#!/bin/sh
PD='/var/lib/prescient/' # must have / at the end

# write out header
echo 'Content-Type: text/html'
echo ''
echo '<html><head><title>prescient</title><meta name="color-scheme" content="light dark"/></head>'
echo '<body><h2>Prescient CI Run Results</h2>'
echo '<ul>'

circle() {
  echo -n "<svg width=\"16\" height=\"16\"><circle cx=\"8\" cy=\"8\" r=\"6\" stroke=\"$1\" fill=\"$1\" /></svg>"
}

dont_understand() {
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
  repos="`ls -1 ${PD}`"
  printf '%s\n' "$repos" | {
    while IFS= read -r repo; do
      echo "<li><a href=\"${SCRIPT_NAME}?repo=${repo}\">${repo}</a></li>"
    done
  }
else
  # list sub repo or result
  for arg in $qargs; do
    IFS="${OIFS}="
    set $arg >/dev/null
    IFS="${OIFS}"

    subdir=$2
    echo "<h3>${subdir}</h3>"

    if [[ "$subdir" = *".."* ]]; then # guard
      dont_understand
    elif [ -z "$subdir"]; then # guard
      dont_understand
    else
      if [ "$1" = "repo" ]; then
        repo_path="${PD}${subdir}"
        repos="`ls -1t ${repo_path}`"
        printf '%s\n' "$repos" | {
          while IFS= read -r repo; do
            rd_path="${repo_path}/${repo}"
            if [ -d "$rd_path" ]; then
              echo "<li><a href=\"${SCRIPT_NAME}?repo=${subdir}/${repo}\">${repo}</a></li>"
            elif [ -f "$rd_path" ]; then
              echo -n '<li>'
              
              unrel=0
              ur_e=0
              errrs="`grep -o -i -E '[0-9]+ errors' ${rd_path} | cut -d' ' -f1`"
              fails="`grep -o -i -E '[0-9]+ failures' ${rd_path} | cut -d' ' -f1`"
              skips="`grep -o -i -E '[0-9]+ skips' ${rd_path} | cut -d' ' -f1`"
              pendg="`grep -o -i -E '[0-9]+ pending' ${rd_path} | cut -d' ' -f1`"

              if [ -z "$errrs" ]; then
                errrs=0
                ur_e=1
              fi
              if [ -z "$fails" ]; then
                fails=0
                if [ 1 -eq $ur_e ]; then
                  unrel=1
                fi
              fi
              if [ -z "$skips" ]; then
                skips=0
              fi
              if [ -z "$pendg" ]; then
                pendg=0
              fi

              if [ 0 -eq $errrs ]; then
                c=0
              else
                c=`echo "$errrs" | wc -l`
              fi
              if [ $c -eq 0 ]; then
                if [ 0 -eq $fails]; then
                  c=0
                else
                  c=`echo "$fails" | wc -l`
                fi
              fi
              if [ $c -eq 0 ]; then
                if [ 0 -eq $skips ]; then
                  c=0
                else
                  c=`echo "$skips" | wc -l`
                fi
              fi
              if [ $c -eq 0 ]; then
                if [ 0 -eq $pendg ]; then
                  c=0
                else
                  c=`echo "$pendg" | wc -l`
                fi
              fi
              
              if [ $c -gt 0 ]; then
                i=1
                while [ $i -le $c ]; do
                  e=`echo "${errrs}" | sed "${i}q;d"`
                  f=`echo "${fails}" | sed "${i}q;d"`
                  s=`echo "${skips}" | sed "${i}q;d"`
                  p=`echo "${pendg}" | sed "${i}q;d"`

                  if [ -n "$e" ] && [ 0 -ne $e ]; then
                    circle 'darkred'
                  elif [ -n "$f" ] && [ 0 -ne $f ]; then
                    circle 'darkred'
                  elif [ -n "$s" ] && [ 0 -ne $s ]; then
                    circle 'darkorange'
                  elif [ -n "$p" ] && [ 0 -ne $p ]; then
                    circle 'darkorange'
                  elif [ 0 -eq $e ] && [ 0 -eq $f ] && [ 0 -eq $s ] && [ 0 -eq $p ] && [ 0 -eq $unrel ]; then
                    circle 'darkgreen'
                  else
                    circle 'darkgrey'
                  fi
                  echo -n "&nbsp;|&nbsp;"
                  i=$((i+2))
                done
              else
                circle 'darkgrey'
              fi
              echo "<a href=\"${SCRIPT_NAME}?file=${subdir}/${repo}\">${repo}</a></li>"
            fi
          done
        }
      elif [ "$1" = "file" ]; then
        file_path="${PD}${subdir}"
        if [ -f "$file_path" ]; then
          echo "<pre>"
          l=0
          while read -r line <&3; do
            l=$(($l+1))
            printf '%6d: ' "$l"
            echo "$line"
          done 3< "$file_path"
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
