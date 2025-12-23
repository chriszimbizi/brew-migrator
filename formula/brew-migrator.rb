class BrewMigrator < Formula
  desc "Migrate applications from /Applications to Homebrew Casks"
  homepage "https://github.com/chriszimbizi/brew-migrator"
  url "https://github.com/chriszimbizi/brew-migrator/archive/refs/tags/v0.0.1.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/brew-migrator", "--help"
  end
end
