import argparse,json,sys
from .common import config

def main():
    parser=argparse.ArgumentParser(description='Reproducible legal NLP experiments')
    parser.add_argument('--config',default='config.yaml')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('download')
    p=commands.add_parser('prepare'); p.add_argument('--full',action='store_true')
    commands.add_parser('baseline')
    p=commands.add_parser('train'); p.add_argument('--task',choices=['classification','summarization'],required=True)
    p=commands.add_parser('evaluate'); p.add_argument('--task',choices=['classification','summarization'],required=True); p.add_argument('--model',choices=['tfidf','legalbert','extractive','t5'],required=True)
    args=parser.parse_args(); cfg=config(args.config)
    if args.command=='download':
        from .data import download
        result=download()
    elif args.command=='prepare':
        from .data import prepare
        result=prepare(cfg,full=args.full)
    elif args.command=='baseline':
        from .training import train_baseline
        result=train_baseline(cfg)
    elif args.command=='train':
        from .training import train_transformer
        result=train_transformer(cfg,args.task)
    else:
        from .experiments import evaluate
        result=evaluate(cfg,args.task,args.model)
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
    try: main()
    except (ValueError,FileNotFoundError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr); sys.exit(2)
