if __name__ == '__main__':
    import peforth
    peforth.ok( loc=locals(),
       glo=globals(),
       cmd =
       '''
       constant parent // ( -- (locals,globals,prompt) ) A tuple about the parent
       '''
       )
