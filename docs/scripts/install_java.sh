#! /bin/bash

install_path="$1"

echo $install_path
# Download java 17
arch=$(uname -i)
echo "Architecture $arch"
if [[ "$arch" == x86_64* ]]; then
  java_url_archive="https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz"
elif  [[ $arch == arm* ]] || [[ $arch = aarch64 ]]; then
  java_url_archive="https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-aarch64_bin.tar.gz"
fi

echo "Download java: $java_url_archive"
curl "$java_url_archive" --output java.tar.gz
mkdir -p $install_path
tar -xzf java.tar.gz -C $install_path



