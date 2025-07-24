class PipelineNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class StepNotFoundError(Exception):
    pass

class DuplicateUserError(Exception):
    pass

class InvalidPasswordError(Exception):
    pass 
class StepIdNotFoundInPipeline(Exception):
    pass