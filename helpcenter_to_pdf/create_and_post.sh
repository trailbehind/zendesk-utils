export PYTHONPATH=../to_json:../localize

python ZendeskPDFMaker.py create

python ZendeskPDFMaker.py post

curl -X POST -H 'Content-type: application/json' --data '{"text":"Manual generation finished."}' $1

