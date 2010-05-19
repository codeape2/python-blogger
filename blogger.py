import rstdirective

def login(username, password):
    import gdata.service
    service = gdata.service.GDataService(username, password)
    service.service = 'blogger'
    service.server = 'www.blogger.com'
    service.ProgrammaticLogin()
    return service

import atom
def create_entry(title, content, draft=False):
    import gdata
    entry = update_entry(gdata.GDataEntry(), title, content)
    if draft:
        control = atom.Control()
        control.draft = atom.Draft(text='yes')
        entry.control = control
    return entry

def update_entry(entry, title, content):
    entry.title = atom.Title(title_type='text', text=title)
    entry.content = atom.Content(content_type='html', text=content.encode('utf8'))
    return entry

def listblogs(service):
    for blogid, title in getblogs(service):
        print "%s: %s" % (blogid, title)

def getblogs(service):
    feed = service.Get('/feeds/default/blogs')
    for blog in feed.entry:
        yield (blog.GetSelfLink().href.split('/')[-1],
            blog.title.text)

def listposts(service, blogid):
    feed = service.Get('/feeds/' + blogid + '/posts/default')
    for post in feed.entry:
        print post.GetEditLink().href.split('/')[-1], post.title.text, "[DRAFT]" if is_draft(post) else ""

def is_draft(post):
    return post.control and post.control.draft and post.control.draft.text == 'yes'

from docutils.examples import html_parts
def read_blogpost(filename, rawhtml, rawhtmltitle):
    if not rawhtml:
        parts = html_parts(open(filename, 'rb').read().decode('utf8'))
        title = parts['title']
        content = parts['body']
    else:
        title = opts.title
        content = open(filename, 'rb').read().decode('utf8')
    return title, content

def dump_blogpost(filename):
    parts = html_parts(open(filename, 'rb').read().decode('utf8'))
    print parts['whole']

USAGE="""
1. python blogger.py --listblogs --username someone@somewhere.com
2. python blogger.py --listposts --username someone@somewhere.com --blog blogid
3. python blogger.py --username someone@somewhere.com --blog blogid filename.rst
4. python blogger.py --username someone@somewhere.com --blog blogid --change postid filename.rst

1. List blogs for user
2. List posts on blog
3. Publish blog post
4. Update an existing post
"""

def parse_command_line():
    import getpass
    from optparse import OptionParser

    parser = OptionParser(usage=USAGE)
    parser.add_option("--username")
    parser.add_option("--password")
    parser.add_option("--blog", metavar="BLOGID")
    parser.add_option("--rawhtml", action="store_true", default=False)
    parser.add_option("--title", help="Only used with --rawhtml")
    parser.add_option("--listblogs", action="store_true", default=False)
    parser.add_option("--listposts", action="store_true", default=False)
    parser.add_option("--change", metavar="POSTID")
    parser.add_option("--dump", action="store_true", default=False, 
        help="Write the HTML output to stdout instead of uploading to blogger")

    opts, args = parser.parse_args()
    if not opts.username and not opts.dump:
        opts.username = raw_input("Username: ")
    if not opts.password and not opts.dump:
        opts.password = getpass.getpass()
    return parser, opts, args

if __name__ == '__main__':
    parser, opts, args = parse_command_line()

    if opts.listblogs:
        listblogs(login(opts.username, opts.password))
    elif opts.listposts:
        listposts(login(opts.username, opts.password), opts.blog)
    else:
        if not args: parser.error("Specify file name")

        if opts.dump:
            dump_blogpost(args[0])
        else:
            title, content = read_blogpost(args[0], opts.rawhtml, opts.title)
            service = login(opts.username, opts.password)
            if opts.change:
                entry = service.Get('/feeds/%s/posts/default/%s' % (opts.blog, opts.change))
                update_entry(entry, title, content)
                service.Put(entry, entry.GetEditLink().href)
            else:
                service.Post(
                    create_entry(title, content),
                    '/feeds/' + opts.blog + '/posts/default')
