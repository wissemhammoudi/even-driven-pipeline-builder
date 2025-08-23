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

class PipelineRunNotFoundError(Exception):
    pass

class StepConfigNotFoundError(Exception):
    pass

class SupersetNotFoundError(Exception):
    pass

class AgenticTransformationNotFoundError(Exception):
    pass

class StepConfigurationAssociationNotFoundError(Exception):
    pass

class PipelineDashboardNotFoundError(Exception):
    pass