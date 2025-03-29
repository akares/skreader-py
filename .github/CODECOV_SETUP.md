# Setting up Codecov Integration

This project uses [Codecov](https://codecov.io/) for code coverage reporting. Follow these steps to set up Codecov integration for your repository:

## 1. Sign up for Codecov

1. Go to [Codecov](https://codecov.io/) and sign in with your GitHub account
2. Add your repository to Codecov by selecting it from the list

## 2. Get your Codecov Token

1. In Codecov, navigate to your repository settings
2. Find the "Repository Upload Token" section
3. Copy the token

## 3. Add the Token to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Create a secret with the name `CODECOV_TOKEN`
5. Paste the token you copied from Codecov as the value
6. Click "Add secret"

## 4. Verify Integration

After you've set up the integration and the GitHub Actions workflow has run:

1. Check that the coverage badge appears in your README
2. Visit your Codecov dashboard to see detailed coverage reports
3. Verify that PRs include coverage feedback from Codecov

If you encounter any issues, check:
- The GitHub Actions logs for any error messages from the Codecov step
- That your repository is correctly configured in Codecov
- That the token is correctly set in your GitHub repository secrets
