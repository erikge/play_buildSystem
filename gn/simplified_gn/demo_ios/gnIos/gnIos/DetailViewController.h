//
//  DetailViewController.h
//  gnIos
//
//  Created by erikge on 15/9/12.
//  Copyright (c) 2015年 erikge. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface DetailViewController : UIViewController

@property (strong, nonatomic) id detailItem;
@property (weak, nonatomic) IBOutlet UILabel *detailDescriptionLabel;

@end

