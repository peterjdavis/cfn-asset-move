import json
import boto3
import argparse
from pathlib import Path

s3_client = boto3.client('s3')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("command", nargs="?")
parser.add_argument(
    "--cfn-input-template",
    help="Location of JSON template to transform [default: template.json].",
    type=Path,
    default=Path("template.json"),
)
parser.add_argument(
    "--cfn-output-template",
    help="Location of JSON template to output [default: template.json].",
    type=Path,
    default=Path("template.json"),
)
parser.add_argument(
    "--target-asset-folder",
    help="Location the assets should be stored [default: ./Assets/].",
    type=Path,
    default=Path("./Assets/"),
)
parser.add_argument(
    "--target_bucket",
    help="Bucket the assets will be stored in.",
)
parser.add_argument(
    "--target_key",
    help="Key the the assets will be stored in.",
)
cli_options = parser.parse_args()

def process_template():

    cfn_input_template = str(cli_options.cfn_input_template)
    cfn_output_template = str(cli_options.cfn_output_template)
    target_asset_folder = str(cli_options.target_asset_folder)
    target_bucket = str(cli_options.target_bucket)
    target_key = str(cli_options.target_key)

    with open(cfn_input_template) as f:
        cfn = json.load(f)
        resources = cfn["Resources"]
        # print(json.dumps(resources, indent=4))

        for key, value in resources.items():
            if value["Type"] == "AWS::Lambda::Function":
                print('Processing: ' + key)
                source_bucket = str(value['Properties']['Code']['S3Bucket'])
                source_key = str(value['Properties']['Code']['S3Key'])
                target_sub_path = '/lambda/'
                s3_client.download_file(source_bucket, source_key, target_asset_folder + target_sub_path + source_key)
                value['Properties']['Code']['S3Bucket'] = target_bucket
                value['Properties']['Code']['S3Key'] = target_key + target_sub_path + source_key
            elif value["Type"] == "AWS::Lambda::LayerVersion": 
                print('Processing: ' + key)
                source_bucket = str(value['Properties']['Content']['S3Bucket'])
                source_key = str(value['Properties']['Content']['S3Key'])
                target_sub_path = '/layer/'
                s3_client.download_file(source_bucket, source_key, target_asset_folder + target_sub_path + source_key)
                value['Properties']['Content']['S3Bucket'] = target_bucket
                value['Properties']['Content']['S3Key'] = target_key + target_sub_path + source_key

    with open(cfn_output_template, 'w') as f:
        json.dump(cfn, f, indent=2)

if __name__ == "__main__":
    cfn_input_template = str(cli_options.cfn_input_template)
    cfn_output_template = str(cli_options.cfn_output_template)
    target_asset_folder = str(cli_options.target_asset_folder)
    target_bucket = str(cli_options.target_bucket)
    target_key = str(cli_options.target_key)
    process_template()
