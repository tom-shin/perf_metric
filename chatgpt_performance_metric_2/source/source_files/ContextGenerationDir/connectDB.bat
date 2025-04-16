title connectDB

icacls "pre-dev-kp-ec2-documentdb.pem" /inheritance:r
icacls "pre-dev-kp-ec2-documentdb.pem" /remove:g "Users" "Authenticated Users" "Everyone" "BUILTIN\Users"
icacls "pre-dev-kp-ec2-documentdb.pem" /grant:r "%USERNAME%:R"


ssh -i "pre-dev-kp-ec2-documentdb.pem" -L 27016:docdb-2025-01-02-06-49-35.cluster-c50g4i88ec8i.ap-northeast-2.docdb.amazonaws.com:27017 ubuntu@ec2-3-34-137-7.ap-northeast-2.compute.amazonaws.com -N
