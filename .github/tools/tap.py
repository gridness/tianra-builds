"""Update only the reviewed CLI formula after hosted archive verification."""
import os
from pathlib import Path
import re
import subprocess


def formula(version, build, checksum):
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('Invalid CLI version')

    if not re.fullmatch(r'[1-9][0-9]{0,14}', build) or not re.fullmatch('[a-f0-9]{64}', checksum):
        raise ValueError('Invalid CLI release identity')

    tag = f'tianra-gm-v{version}-build.{build}'
    asset = f'tianra-gm-{version}-build-{build}-macos-aarch64.tar.gz'
    return f'''class TianraGm < Formula
  desc "Tianra Game Master tools for AI agents and humans"
  homepage "https://github.com/gridness/tianra-builds"
  version "{version}.{build}"

  depends_on macos: :sequoia
  depends_on arch: :arm64

  url "https://github.com/gridness/tianra-builds/releases/download/{tag}/{asset}"
  sha256 "{checksum}"

  def install
    bin.install "bin/tianra-gm"
    pkgshare.install "version.json", "licenses"
    generate_completions_from_executable(bin/"tianra-gm", "completions", shells: [:bash, :zsh, :fish])
  end

  def caveats
    <<~EOS
      Uses the installed SpacetimeDB CLI sign-in. Tool data stays in ~/.tianra-gm.
      Install the bundled agent skill explicitly:
        tianra-gm skill install --agent codex
        tianra-gm skill install --agent claude
    EOS
  end

  test do
    assert_match "{version}", shell_output("#{{bin}}/tianra-gm --version")
    assert_match '"schema_version":1', shell_output("#{{bin}}/tianra-gm commands")
  end
end
'''


if __name__ == '__main__':
    destination = Path('Formula/tianra-gm.rb')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(formula(os.environ['CLI_VERSION'], os.environ['CLI_BUILD'], os.environ['CLI_SHA256']))
    subprocess.run(['git', 'add', '--', str(destination)], check=True)
