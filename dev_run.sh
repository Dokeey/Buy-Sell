docker run \
    -p 8000:8000 \
    -e AZURE_ACCOUNT_NAME="buynsells" \
    -e AZURE_ACCOUNT_KEY="vZOWhOqN0kRTPJ9nFGnKtvYIivqsJwHZC6JtMQwaiJvw4TKF24nNkz5aKMBMQfmv1s/uKH4gf8SStYt5ZssiHw==" \
    -e DB_HOST="bnsdb.postgres.database.azure.com" \
    -e DB_NAME="postgres" \
    -e DB_USER="bns@bnsdb" \
    -e DB_PASSWORD="wjdqhqhdks1!" \
    -v $(pwd)/.:/bns \
    --rm -it -d \
    ehdgnv/bns-dev:1.0