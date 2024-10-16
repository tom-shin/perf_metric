icacls "LOC-docdb.pem" /inheritance:r /grant %username%:RW /remove "Users"

ssh -i "LOC-docdb.pem" -L 27017:dev-local-docdb-2024-07-23-08-10-47.cluster-cfmi4emkmqvg.ap-northeast-2.docdb.amazonaws.com:27017 ubuntu@ec2-3-34-157-40.ap-northeast-2.compute.amazonaws.com -N



