export PYTHONPATH=../to_json:../localize
#python ZendeskPDFMaker.py create
#python ZendeskPDFMaker.py post

slack_url=$1
if [[ -n "$slack_url" ]]; then
curl -X POST -H 'Content-type: application/json' --data '{"text":"Manual generation finished."}' $slack_url
else
echo "no slack url given for manual update notif"
fi


