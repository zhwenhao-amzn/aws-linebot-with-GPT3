
# Linebot with OpenAI GPT3 on AWS

This repository is the result of my collaboration with OpenAI GPT-4 model, and it includes how to deploy resources using Node.js serverless architecture.

## Usage

### Deployment

```
$ serverless deploy
```

After deploying, you should see output similar to:

```bash
Deploying aws-linebot-with-GPT3 to stage dev (us-east-1)

✔ Service deployed to stack aws-linebot-with-GPT3 (140s)

endpoint: GET - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/
functions:
  hello: aws-python-http-api-project-dev-hello (2.3 kB)
```

After deploying the resources, you need to register API gatway endpoint as the line bot webhook url, and configure *Opan AI kay* 、 *line channel secret* and * line channel token* in lambda environemnt.


### Bundling dependencies

In case you would like to include 3rd party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
