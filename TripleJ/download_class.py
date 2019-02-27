from gevent import monkey
#monkey.patch_all()
from gevent.pool import Pool
import uuid
import os
import m3u8
import requests
import subprocess
import shutil

class ABCDownloader:

    def __init__(self, pool_size, retry=3):
        self.pool = Pool(pool_size)
        self.session = self._get_http_session(pool_size, pool_size, retry)
        self.retry = retry
        self.dir = ''
        self.succeed = {}
        self.failed = []
        self.total_segments = 0
        self.files = []
        self.master_url = "https://abcradiomodhls-vh.akamaihd.net/i/triplej/audio/mix-2019-02-16-1-final.m4a/master.m3u8"
        self.master_file = "master.m3u8"
        self.html_url = ''
        self.index_url = ''
        self.index_file = "index_0_a.m3u8"
        self.output_file = ''
        self.output_m4a = ''
        self.final_name = 'Mixup.m4a'


    def _get_http_session(self, pool_connections, pool_maxsize, max_retries):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections,
                                                pool_maxsize=pool_maxsize,
                                                max_retries=max_retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    

    def run(self, m3u8_url):
        dir = str(uuid.uuid4())
        self.dir = os.path.join('data', dir)
        os.mkdir(self.dir)
        self.master_file = os.path.join(self.dir, self.master_file)
        self.download_m1_file()
        self.download_m2_files()
        self.download_segments_as_pool()
        self.add_names_hack()
        self.join_files()
        self.convert_ts_to_m4a()
        return self.output_m4a, self.dir


    def download_url(self, curr_url, file_name):
        r = requests.get(curr_url, stream=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        return file_name


    def add_names_hack(self):
        '''
        I don't know enough about gevent concurrency, but I'm assuming if I had
        simply added the filenames when running '_worker' that the operation would
        be anything _but_ thread-safe and fuck everything up. This creates it instead.
        '''
        _i_index = 0
        for i in range(self.total_segments):
            _i_index += 1
            name = 'segment_' + str(_i_index) + '.ts'
            full_name = os.path.join(self.dir, name)
            self.files.append(full_name)


    def join_files(self):
        print("Joining files")
        output_file = "output.ts"
        outfile = open(os.path.join(self.dir, output_file), 'wb')
        self.output_file = os.path.join(self.dir, output_file)
        for i in self.files:
            infile = open(i, 'rb')
            outfile.write(infile.read())
            infile.close()
        outfile.close()


    def download_m1_file(self):
        self.download_url(self.master_url, self.master_file)


    def download_m2(self):
        m3u8_obj = m3u8.load(os.path.join(instance_dir, m3file_1))
        playlist = m3u8_obj.playlists[0]
        global url_final
        url_final = playlist.absolute_uri
        self.download_url(url_final, m3file_2)


    def download_m2_files(self):
        m3u8_obj = m3u8.load(self.master_file)
        playlist = m3u8_obj.playlists[0]
        self.index_url = playlist.absolute_uri
        self.download_url(self.index_url, self.index_file)


    def download_segments_as_pool(self):
        m3u8_obj = m3u8.load(self.index_file)
        segments = m3u8_obj.segments
        urls = []
        files = []
        for i in segments:
            urls.append(i.uri)
        self.total_segments = urls.__len__()
        print (str(self.total_segments) + " segments found")
        ts_list = zip(urls, [n for n in range(len(urls))])
        self.pool.map(self._worker, ts_list)


    def _worker(self, ts_tuple):
        url = ts_tuple[0]
        index = ts_tuple[1]
        index += 1

        print("Downloading " + str(index) + " of " + str(self.total_segments))

        r = self.session.get(url, timeout=20)
        if r.ok:
            file_name = 'segment_' + str(index) + '.ts'
            with open(os.path.join(self.dir, file_name), "wb") as f:
                f.write(r.content)
            self.succeed[index] = file_name
        return


    def download_segments(self):
        m3u8_obj = m3u8.load(os.path.join(instance_dir, m3file_2))
        segments = m3u8_obj.segments
        urls = []
        files = []
        for i in segments:
            urls.append(i.uri)
        print (str(urls.__len__()) + " segments found")

        _i_index = 0
        for i in urls:
            _i_index += 1
            print("Downloading " + str(_i_index) + " of " + str(urls.__len__()))
            name = 'segment_' + str(_i_index) + '.ts'
            files.append(download_url(i, name))
        join_files(files)

    def convert_ts_to_m4a(self):
        '''
        requires ffmpeg to be installed
        '''
        output_m4a = os.path.join(self.dir, self.final_name)
        self.output_m4a = output_m4a
        command = ("ffmpeg -i " + self.output_file + " -bsf:a aac_adtstoasc -acodec copy -vcodec copy " + output_m4a)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()

    def delete(self):
        shutil.rmtree(self.dir)

if __name__ == "__main__":
    downloader = ABCDownloader(pool_size=40)
    downloader.run("https://abcradiomodhls-vh.akamaihd.net/i/triplej/audio/mix-2019-02-16-1-final.m4a/master.m3u8")