from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os
import requests

required_conan_version = ">=1.36.0"


class ClipperConan(ConanFile):
    name = "clipper"
    description = "Clipper is an open source freeware polygon clipping library"
    topics = ("clipper", "clipping", "polygon")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.angusj.com/delphi/clipper.php"
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @staticmethod
    def _generate_git_tag_archive_sourceforge(url, timeout=10, retry=2):
        def try_post(retry_count):
            try:
                requests.post(url, timeout=timeout)
            except:
                if retry_count < retry:
                    try_post(retry_count + 1)
                else:
                    raise ConanException("All the attempt to generate archive url have failed.")
        try_post(0)

    def source(self):
        conan_data_version = self.conan_data["sources"][self.version]
        if "post" in conan_data_version["url"]:
            # Generate the archive download link
            self._generate_git_tag_archive_sourceforge(
                conan_data_version["url"]["post"],
            )

            # Download archive
            archive_url = conan_data_version["url"]["archive"]
            sha256 = conan_data_version["sha256"]
            tools.get(url=archive_url, sha256=sha256,
                      destination=self._source_subfolder, strip_root=True)
        else:
            tools.get(**conan_data_version, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # To install relocatable shared libs on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "polyclipping")
        self.cpp_info.libs = ["polyclipping"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed.
        #       Do not use these CMake names in CMakeDeps, it was a mistake,
        #       clipper doesn't provide CMake config file
        self.cpp_info.names["cmake_find_package"] = "polyclipping"
        self.cpp_info.names["cmake_find_package_multi"] = "polyclipping"
        self.cpp_info.names["pkg_config"] = "polyclipping"
