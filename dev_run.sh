docker run \
    -p 8000:80 \
    -e AZURE_ACCOUNT_NAME="buynsell" \
    -e AZURE_ACCOUNT_KEY="CD/QgNx6YJWbnGGBp9qu+aROr8qSIFcS5We9rbUfNzAhLeIj3NewbnSpbbqfD92/Ns4r2pRIAmxe3myrKbNDxQ==" \
    -e DB_HOST="buynsell.postgres.database.azure.com" \
    -e DB_NAME="postgres" \
    -e DB_USER="bns@buynsell" \
    -e DB_PASSWORD="wjdqhqhdks1!" \
    --rm -it \
    ehdgnv/bns-azure:1.0 sh