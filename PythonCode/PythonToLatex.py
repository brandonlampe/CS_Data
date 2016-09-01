import Table
fout = open('mytable.tex','w')
t = Table.Table(numcols=3,
                justs='lrc',
                caption='Awesome results',
                label="tab:label")
t.add_header_row(['obj', 'X', '$\\beta$'])
col1 = ['obj1','obj2','obj3']
col2 = [0.001,0.556,10.56]   # just numbers
col3 = [[0.12345,0.1],[0.12345,0.01],[0.12345,0.001]]
t.add_data([col1,col2,col3], sigfigs=2)
t.print_table(fout)
fout.close()
