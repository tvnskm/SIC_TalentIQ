class TalentIQBaseException(Exception):
    """Base exception for all TalentIQ errors."""
    pass

class ResumeProcessingError(TalentIQBaseException):
    pass

class SkillExtractionError(TalentIQBaseException):
    pass

class MatchingEngineError(TalentIQBaseException):
    pass

class InvalidFileFormatError(TalentIQBaseException):
    pass

class FileSizeTooLargeError(TalentIQBaseException):
    pass

class DuplicateCandidateError(TalentIQBaseException):
    pass

class JobNotFoundError(TalentIQBaseException):
    pass

class CandidateNotFoundError(TalentIQBaseException):
    pass
