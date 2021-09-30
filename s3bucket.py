from troposphere import Ref, Template
from troposphere.s3 import (
    Bucket,
    LifecycleConfiguration,
    LifecycleRule,
    LifecycleRuleTransition,
    NoncurrentVersionTransition,
    PublicRead,
    VersioningConfiguration,
)


def create_s3_bucket(template, bucket_name):
    s3_bucket = template.add_resource(
        Bucket(
            "S3Bucket",
            BucketName=Ref(bucket_name),
            AccessControl="Private",
            VersioningConfiguration=VersioningConfiguration(
                Status="Enabled",
            ),
            # Attach a LifeCycle Configuration
            LifecycleConfiguration=LifecycleConfiguration(
                Rules=[

                    LifecycleRule(
                        # Rule attributes
                        Id="S3BucketRule001",
                        Prefix="/",
                        Status="Enabled",
                        # Applies to current version of the objects
                        ExpirationInDays=365,
                        Transitions=[
                            LifecycleRuleTransition(
                                StorageClass="STANDARD_IA",
                                TransitionInDays=60,
                            ),
                        ],
                        # Applies to Non Current version of the  objects
                        NoncurrentVersionExpirationInDays=365,
                        NoncurrentVersionTransitions=[
                            NoncurrentVersionTransition(
                                StorageClass="STANDARD_IA",
                                TransitionInDays=30,
                            ),
                            NoncurrentVersionTransition(
                                StorageClass="GLACIER",
                                TransitionInDays=120,
                            ),
                        ],
                    ),
                ]
            ),
        )
    )
    return s3_bucket
