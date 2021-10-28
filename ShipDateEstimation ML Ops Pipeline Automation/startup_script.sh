#! /bin/bash
ROLE=$(/usr/share/google/get_metadata_value attributes/dataproc-role)
REMOTE_EXECUTION_FILE_PATH=$(/usr/share/google/get_metadata_value attributes/remoteExecutionFilePath)
USER_NAME=$(/usr/share/google/get_metadata_value attributes/userName)
KEY_SAVE_PATH=$(/usr/share/google/get_metadata_value attributes/keySavePath)
DATA_ORIGIN_PATH=$(/usr/share/google/get_metadata_value attributes/dataOriginPath)
DATA_DESTINATION_PATH=$(/usr/share/google/get_metadata_value attributes/dataDestinationPath)
DATA_ARCHIVE_PATH=$(/usr/share/google/get_metadata_value attributes/dataArchivePath)
if [[ "${ROLE}" == 'Master' ]]; then
    ##Create User specific keys and copy the keys to cloud bucket
    ssh-keygen -m PEM -t rsa -b 4096 -f ~/.ssh/remoteKey -C ${USER_NAME} -q -P ""
    cd ~/.ssh
    sudo gsutil cp remote* ${KEY_SAVE_PATH}
    ## Copy files required for later remote execution to data proc master VM
    cd /home
    sudo gsutil -m cp -r ${REMOTE_EXECUTION_FILE_PATH} .
    sudo chmod 755 *
    ##Create Directory and Copy data to directory
    sudo mkdir inbounddata
    cd /home/inbounddata
    sudo gsutil -m cp -r ${DATA_ORIGIN_PATH} .
    ##gunzip the data
    sudo gunzip *

    ##remove or convert non ascii characters to ascii
    for file in *.csv 
    do 
        charset=$(file -bi "$file" | grep -o 'charset.*'|cut -f2- -d=)
        echo ${charset}
        sudo bash -c "sudo iconv -c -f "${charset}" -t ascii//TRANSLIT "$file" > "$file.new""
        sudo chmod 775 *
        sudo mv -f "$file.new" "$file" 
    done

    ##Move to Cloud Storage
    sudo gsutil -m mv *.csv ${DATA_DESTINATION_PATH}

    ##Remove temporary directory
    cd /home
    sudo rm -r inbounddata

    ##Move processed files to archive
    sudo gsutil -m mv ${DATA_ORIGIN_PATH} ${DATA_ARCHIVE_PATH}
fi