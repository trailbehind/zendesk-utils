import sys
from helpcenter_to_pdf.ZendeskPDFMaker import ZendeskPDFMaker

def print_usage():
    print("\nparameters are: create, post, ping_slack, run\n")
    
zdpm = ZendeskPDFMaker()
if len(sys.argv) < 2:
    print_usage()
    sys.exit(2)

if sys.argv[1] == 'create':
  zdpm.create_pdfs()
elif sys.argv[1] == 'post':
  zdpm.post_pdfs_to_s3()
elif sys.argv[1] == 'ping_slack':
  zdpm.ping_slack()
elif sys.argv[1] == 'run':
    zdpm.create_pdfs()
    zdpm.post_pdfs_to_s3()
    if SLACK_NOTIFICATION_URL:
      zdpm.ping_slack()
else:
  print_usage()