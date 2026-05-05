#!/usr/bin/env sh
set -eu

if ! command -v tlmgr >/dev/null 2>&1; then
  cat >&2 <<'EOF'
tlmgr is not available. Install a fuller TeX Live/MacTeX distribution, then rerun:

  make wiley-tex-deps

EOF
  exit 2
fi

packages="dashrule multirow sttools dblfloatfix soul xargs tcolorbox varwidth tikzpagenodes boites wrapfig footmisc stix2-type1 ifoddpage algorithmicx"
missing=""
for package in $packages; do
  sty="$package.sty"
  if [ "$package" = "sttools" ]; then
    sty="cuted.sty"
  elif [ "$package" = "stix2-type1" ]; then
    sty="stix2.sty"
  elif [ "$package" = "algorithmicx" ]; then
    sty="algpseudocode.sty"
  fi
  if ! kpsewhich "$sty" >/dev/null 2>&1; then
    missing="$missing $package"
  fi
done

if [ -z "$missing" ]; then
  echo "Wiley TeX dependencies are already installed."
  exit 0
fi

echo "Installing missing Wiley TeX packages into the user TeX tree:$missing"
tlmgr init-usertree >/dev/null 2>&1 || true
tlmgr --usermode install $missing
