import os
import shutil
import requests
import threading
from . import civitai
from . import util
from . import downloader
from . import setting
    
def download_file_thread(file_name, version_id, lora_an):               
    if not file_name:
        return

    if not version_id:
        return
    
    version_info = civitai.get_version_info_by_version_id(version_id)
    
    if not version_info:
        return 
       
    download_files = civitai.get_files_by_version_info(version_info)
    
    if not download_files:
        return

    model_folder = util.make_model_folder(version_info['model']['type'], version_info['model']['name'], lora_an)
    
    if not model_folder:
        return
                
    for file in file_name:                    
        try:
            #모델 파일 저장
            path_dl_file = os.path.join(model_folder, file)            
            thread = threading.Thread(target=downloader.download_file,args=(download_files[file]['downloadUrl'], path_dl_file))                        
            # Start the thread
            thread.start()                

            # 버전 인포 파일 저장. primary 이름으로 저장한다.
            info_file = civitai.write_version_info_by_version_info(model_folder,version_info)
            if info_file:
                util.printD(f"Wrote version info : {info_file}")

        except:
            pass

    # triger words 가 있으면 저장. primary 이름으로 저장한다.
    triger_file = civitai.write_triger_words_by_version_info(model_folder,version_info)
    if triger_file:
         util.printD(f"Wrote triger words : {triger_file}")

    return f"Download started"

def download_image_files(version_id, lora_an):
    message =""
    base = None
    
    if not version_id:                
        return         
    
    version_info = civitai.get_version_info_by_version_id(version_id)          
    
    if not version_info:
        return
    
    if 'images' not in version_info.keys():
        return
        
    model_folder = util.make_model_folder(version_info['model']['type'], version_info['model']['name'], lora_an)
    
    if not model_folder:
        return
    
    # 이미지 파일명도 primary 이름으로 저장한다.
    primary_file = civitai.get_primary_file_by_version_info(version_info)
    if not primary_file:
        #없으면 임의로 만들어준다
        base = util.replace_filename(version_info['model']['name'] + "." + version_info['name'])
    base, ext = os.path.splitext(primary_file['name'])                    
    base = os.path.join(setting.root_path, model_folder, base)
    
    if base and len(base.strip()) > 0:                                           
        image_count = 0           
        for img_dict in version_info["images"]:
            # if "nsfw" in img_dict:
            #     if img_dict["nsfw"]:
            #         printD("This image is NSFW")

            if "url" in img_dict:
                img_url = img_dict["url"]
                # use max width
                if "width" in img_dict:
                    if img_dict["width"]:
                        img_url =  util.change_width_from_image_url(img_url, img_dict["width"])
                
                try:
                    # get image
                    with requests.get(img_url, stream=True) as img_r:
                        if not img_r.ok:
                            util.printD("Get error code: " + str(img_r.status_code) + ": proceed to the next file")
                            continue

                        # write to file
                        description_img = f'{base}_{image_count}.preview.png'
                        if image_count == 0:
                            description_img = f'{base}.preview.png'
                                                                                
                        with open(description_img, 'wb') as f:
                            img_r.raw.decode_content = True
                            shutil.copyfileobj(img_r.raw, f)
                except Exception as e:
                    pass
                
                # set image_counter
                image_count = image_count + 1
    
        if image_count > 2:        
            message = f"Downloaded {image_count} images"
        else:
            message = f"Downloaded image"                    
    return message       

def get_model_title_name_by_version_id(version_id:str)->str:
    if not version_id:
        return
    
    info = civitai.get_version_info_by_version_id(version_id)
    return get_model_title_name_by_version_info(info)

def get_model_title_name_by_version_info(version_info:dict)->str:
    if not version_info:
        return
    
    title_name = ""
    if 'model' not in version_info:
        return
        
    title_name = f"### {version_info['model']['name']} : {version_info['name']}"
    return title_name

def get_version_description_gallery_by_version_info(version_info:dict):       
    if not version_info:
        return None,None

    version_images = []
    version_images_url = []
    version_full_images_url = []

    if 'images' not in version_info:
        return None,None
                    
    for pic in version_info["images"]:   
        if "url" in pic:
            img_url = pic["url"]
            # use max width
            # 파일 인포가 있는 원본 이미지.
            if "width" in pic:
                if pic["width"]:
                    img_url = util.change_width_from_image_url(img_url, pic["width"])                                            

            # 파일 이상 유무 체크 하지만!!!! 속도는?
            # 일단 이걸로 간다.
            # 문제있는 파일은 건너뛴다.                   
            # try:
            #     img_r = requests.get(pic["url"],stream=True)
            #     if not img_r.ok:
            #         util.printD("Get error code: " + str(img_r.status_code) + ": proceed to the next file")            
            #         continue
            #     img_r.raw.decode_content=True
            #     version_images.append(Image.open(img_r.raw))        
            #     version_full_images_url.append(img_url)                                  
            # except:
            #     pass

            #작은 이미지 - 로드는 작은 이미지로 한다
            #제네레이션 정보는 원본에만 있다                        
            #version_images_url.append((pic["url"],f"[{version_info['id']}]:{version_info['model']['name']}"))
            version_images_url.append(pic["url"])
            version_full_images_url.append(img_url)     
                
    return version_images_url,version_full_images_url
    # return version_images,version_full_images_url

def get_version_description_gallery_by_version_id(version_id:str):       
    if not version_id:                
        return None,None
    
    # util.printD(f"{version_id}")
    
    version_info = civitai.get_version_info_by_version_id(version_id)
    return get_version_description_gallery_by_version_info(version_info)

def get_version_description_by_version_info(version_info:dict):
    output_html = ""
    output_training = ""

    files_name = []
    
    html_typepart = ""
    html_creatorpart = ""
    html_trainingpart = ""
    html_modelpart = ""
    html_versionpart = ""
    html_descpart = ""
    html_dnurlpart = ""
    html_imgpart = ""
    html_modelurlpart = ""
    
    model_id = None
    
    if not version_info:
        return "",None,None,None
    
    if 'modelId' not in version_info:
        return "",None,None,None
        
    model_id = version_info['modelId']
    
    if not model_id:
        return "",None,None,None
        
    model_info = civitai.get_model_info_by_model_id(model_id)

    if not model_info:
        return "",None,None,None
                
    html_typepart = f"<br><b>Type: {model_info['type']}</b>"    
    model_url = civitai.Url_Page()+str(model_id)

    html_modelpart = f'<br><b>Model: <a href="{model_url}" target="_blank">{model_info["name"]}</a></b>'
    html_modelurlpart = f'<br><b><a href="{model_url}" target="_blank">Civitai Hompage << Here</a></b><br>'

    model_version_name = version_info['name']

    if 'trainedWords' in version_info:  
        output_training = ", ".join(version_info['trainedWords'])
        html_trainingpart = f'<br><b>Training Tags:</b> {output_training}'

    model_uploader = model_info['creator']['username']
    html_creatorpart = f"<br><b>Uploaded by:</b> {model_uploader}"

    if 'description' in version_info:  
        if version_info['description']:
            html_descpart = f"<br><b>Version : {version_info['name']} Description</b><br>{version_info['description']}<br>"
            
    if 'description' in model_info:  
        if model_info['description']:
            html_descpart = html_descpart + f"<br><b>Description</b><br>{model_info['description']}<br>"
                
    html_versionpart = f"<br><b>Version:</b> {model_version_name}"

    # html_imgpart = "<div with=100%>"
    # for pic in version_info['images']:
    #      image_url = util.change_width_from_image_url(pic["url"], pic["width"])
    #      html_imgpart = html_imgpart + f'<img src="{image_url}" width=200px></img>'                            
    # html_imgpart = html_imgpart + '</div><br>'

    if 'files' in version_info:                                
        for file in version_info['files']:
            files_name.append(file['name'])
            html_dnurlpart = html_dnurlpart + f"<br><a href={file['downloadUrl']}><b>Download << Here</b></a>"     
                        
    output_html = html_typepart + html_modelpart + html_versionpart + html_creatorpart + html_trainingpart + "<br>" +  html_modelurlpart + html_dnurlpart + "<br>" + html_descpart + "<br>" + html_imgpart
    
    return output_html, output_training, [v for v in files_name], model_info['type']     

def get_version_description_by_version_id(version_id=None):
    if not version_id:
        return "",None,None    
    version_info = civitai.get_version_info_by_version_id(version_id)    
    return get_version_description_by_version_info(version_info)        


# url에서 model info 정보를 반환한다
def get_selected_model_info_by_url(url:str):
    model_id = None
    model_name = None
    model_type = None
    def_id = None
    def_name = None
    def_image = None
    model_url = None
    
    versions_list = []
    if url:  
        model_id = util.get_model_id_from_url(url) 
        model_info = civitai.get_model_info_by_model_id(model_id)
        if model_info:
            versions_list = []
            model_id = model_info['id']
            model_name = model_info['name']
            model_type = model_info['type']
            model_url = f"{civitai.Url_ModelId()}{model_id}"
            
            if "modelVersions" in model_info.keys():            
                def_version = model_info["modelVersions"][0]
                def_id = def_version['id']
                def_name = def_version['name']
                
                if 'images' in def_version.keys():
                    if len(def_version["images"]) > 0:
                        img_dict = def_version["images"][0]
                        def_image = img_dict["url"]
                                                                
                for version_info in model_info['modelVersions']:
                    versions_list.append(version_info['name'])                        
        
    return model_id, model_name, model_type, model_url, def_id, def_name, def_image ,[v for v in versions_list]

