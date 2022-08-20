class MazelException(Exception):
    pass


class PackageNotFound(MazelException):
    pass


class RuntimeNotFound(MazelException):
    pass


# class InvalidLabel(MazelException):
#     pass


class DuplicateDependency(MazelException):
    pass


class InvalidBuildToml(MazelException):
    pass


class InvalidPackage(MazelException):
    pass
